"""Load typed order lines, execute SQL and export source-backed customer evidence.

Run from the repository root: python -m sql.run_analysis
Only the standard library is needed; analytical calculations live in .sql files.
"""

import argparse
import csv
from datetime import date, datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[1]
SQL_ROOT = Path(__file__).resolve().parent


def money_micros(value: str) -> int:
    """Keep source amounts exact; reject values needing more than six decimals."""
    amount = Decimal(value) * 1_000_000
    if not amount.is_finite() or amount != amount.to_integral_value():
        raise ValueError(f"Invalid monetary amount: {value}")
    return int(amount)


def build_database(source: Path, as_of: str | None = None) -> sqlite3.Connection:
    """Fail on invalid identifiers, dates or inconsistent order attributes."""
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript((SQL_ROOT / "schema.sql").read_text())
    try:
        with source.open(encoding="latin1", newline="") as handle:
            for row in csv.DictReader(handle):
                identifiers = [row[k].strip() for k in ("Order ID", "Customer ID", "Region", "Segment")]
                if not all(identifiers):
                    raise ValueError("Order/customer identifiers and dimensions cannot be empty")
                order_id, customer_id, region, segment = identifiers
                order_date = datetime.strptime(row["Order Date"], "%m/%d/%Y").date().isoformat()
                connection.execute(
                    "INSERT INTO order_lines VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (int(row["Row ID"]), order_id, customer_id, order_date, region, segment,
                     money_micros(row["Sales"]), money_micros(row["Profit"]),
                     int(row["Quantity"]), float(row["Discount"])),
                )
        invalid = connection.execute(
            "SELECT order_id FROM order_lines GROUP BY order_id "
            "HAVING COUNT(DISTINCT customer_id) != 1 OR COUNT(DISTINCT order_date) != 1 "
            "OR COUNT(DISTINCT region) != 1 OR COUNT(DISTINCT segment) != 1"
        ).fetchone()
        if invalid:
            raise ValueError(f"Inconsistent order attributes: {invalid['order_id']}")
        start, end = connection.execute("SELECT MIN(order_date), MAX(order_date) FROM order_lines").fetchone()
        if end is None:
            raise ValueError("Source has no orders")
        cutoff = date.fromisoformat(as_of).isoformat() if as_of else end
        if not start <= cutoff <= end:
            raise ValueError("as_of must lie within the observed date range")
        connection.execute("INSERT INTO analysis_scope VALUES (?)", (cutoff,))
        connection.commit()
        return connection
    except Exception:
        connection.close()
        raise


def run_query(connection: sqlite3.Connection, filename: str) -> list[dict]:
    return [dict(row) for row in connection.execute((SQL_ROOT / "queries" / filename).read_text())]


def analyze(source: Path, output: Path, as_of: str | None = None) -> dict:
    """Export deterministic CSVs and a source hash; leave the database uncommitted."""
    output.mkdir(parents=True, exist_ok=True)
    connection = build_database(source, as_of)
    try:
        results = {}
        for query in sorted((SQL_ROOT / "queries").glob("*.sql")):
            cursor = connection.execute(query.read_text())
            rows = [dict(row) for row in cursor]
            results[query.stem] = rows
            with (output / (query.stem + ".csv")).open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[column[0] for column in cursor.description])
                writer.writeheader()
                writer.writerows({k: format(v, '.12g') if isinstance(v, float) else v
                                  for k, v in row.items()} for row in rows)
        totals = results["01_reconciliation"][0]
        raw = connection.execute(
            "SELECT COUNT(*) AS lines, SUM(sales_micros) AS sales, SUM(profit_micros) AS profit "
            "FROM order_lines WHERE order_date <= ?", (totals["as_of"],)
        ).fetchone()
        if (totals["order_lines"], totals["sales_micros"], totals["profit_micros"]) != tuple(raw):
            raise ValueError("Order-grain amounts do not reconcile to source lines")
        manifest = {
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "sqlite_version": sqlite3.sqlite_version,
            "schema_sha256": hashlib.sha256((SQL_ROOT / "schema.sql").read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": totals,
            "repeat_purchase_90d": results["04_repeat_purchase_90d"][0],
            "query_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted((SQL_ROOT / "queries").glob("*.sql"))},
            "definitions": {
                "cohort": "first observed order month; not verified customer acquisition",
                "monthly_retention": "distinct cohort customers active in a fully observable calendar month / cohort size",
                "repeat_90d": "a second distinct order within 90 days; only full 90-day observation windows",
                "same_day_orders": "distinct order IDs count as purchases; date ties ordered by order ID",
                "coverage": "a sample snapshot; absence of a purchase is not proof of inactivity in the full business",
            },
        }
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        return manifest
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "data" / "Sample - Superstore.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "sql")
    parser.add_argument("--as-of", help="ISO date within the observed source window")
    args = parser.parse_args()
    print(json.dumps(analyze(args.source, args.output, args.as_of), indent=2))


if __name__ == "__main__":
    main()
