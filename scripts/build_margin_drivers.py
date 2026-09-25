"""Rebuild the committed driver evidence from the original Superstore CSV."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from analysis.margin_drivers import analyze


ROOT = Path(__file__).resolve().parents[1]


def write_table(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "data" / "Sample - Superstore.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs")
    parser.add_argument("--focus", default="Central")
    parser.add_argument("--reference", default="West")
    args = parser.parse_args()
    with args.source.open(newline="", encoding="latin1") as handle:
        result = analyze(list(csv.DictReader(handle)), args.focus, args.reference)
    args.output.mkdir(parents=True, exist_ok=True)
    write_table(args.output / "product_margin_contributions.csv", result.pop("product_rows"))
    write_table(args.output / "shipping_mode_contributions.csv", result.pop("shipping_rows"))
    write_table(args.output / "discount_diagnostic.csv", result.pop("discount_rows"))
    result["source_sha256"] = hashlib.sha256(args.source.read_bytes()).hexdigest()
    result["method"] = "Sales-weighted Shapley accounting decomposition; percentage points, reference to focus"
    result["interpretation"] = "Product and shipping are alternative, non-additive views; discount is descriptive, not causal"
    (args.output / "margin_drivers.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{args.reference} to {args.focus}: {result['gap_pp']:.4f} pp; product and shipping views reconcile.")


if __name__ == "__main__":
    main()
