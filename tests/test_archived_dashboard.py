"""The archived HTML dashboard must agree with the committed source data."""

import ast
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "docs" / "shipping_region_analysis.html").read_text(encoding="utf-8")
MODES = ["Same Day", "First Class", "Second Class", "Standard Class"]


def js_literal(name):
    match = re.search(rf"const {name}=(\[\[.*?\]\])", HTML)
    return ast.literal_eval(match.group(1))


class ArchivedDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "data" / "Sample - Superstore.csv").open(newline="", encoding="latin1") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_margin_heatmap_matches_source(self):
        totals = defaultdict(lambda: [0.0, 0.0])
        for row in self.rows:
            cell = totals[row["Region"], row["Ship Mode"]]
            cell[0] += float(row["Sales"])
            cell[1] += float(row["Profit"])
        for region, *margins in js_literal("rows"):
            for mode, shown in zip(MODES, margins):
                sales, profit = totals[region, mode]
                self.assertAlmostEqual(shown, round(profit / sales * 100, 2), places=2,
                                       msg=f"{region} / {mode}")

    def test_dispatch_counts_use_distinct_orders(self):
        orders = {}
        for row in self.rows:
            if row["Ship Mode"] == "Standard Class":
                ordered = datetime.strptime(row["Order Date"], "%m/%d/%Y")
                shipped = datetime.strptime(row["Ship Date"], "%m/%d/%Y")
                orders[row["Order ID"]] = (row["Region"], (shipped - ordered).days)
        for region, late, percent in js_literal("late"):
            days = [d for r, d in orders.values() if r == region]
            dispatched_late = sum(d > 5 for d in days)
            self.assertEqual(late, dispatched_late, region)
            self.assertAlmostEqual(percent, round(dispatched_late / len(days) * 100, 2), places=2)

    def test_header_reports_orders_and_lines(self):
        self.assertIn(f"{len({r['Order ID'] for r in self.rows}):,} Orders", HTML)
        self.assertIn(f"{len(self.rows):,} order lines", HTML)


if __name__ == "__main__":
    unittest.main()
