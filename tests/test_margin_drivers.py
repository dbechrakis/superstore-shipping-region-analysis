"""Invariants for the product and shipping accounting views."""

import csv
from math import isclose
from pathlib import Path
import unittest

from analysis.margin_drivers import analyze


ROOT = Path(__file__).resolve().parents[1]


def row(region, category, subcategory, mode, sales, profit, discount=0):
    return {"Row ID": "1", "Region": region, "Category": category,
            "Sub-Category": subcategory, "Ship Mode": mode, "Sales": sales,
            "Profit": profit, "Discount": discount}


class MarginDriverTests(unittest.TestCase):
    def test_pure_category_mix_and_exact_reconciliation(self):
        rows = [
            row("West", "A", "a", "Standard", 50, 10),
            row("West", "B", "b", "First", 50, 0),
            row("Central", "A", "a", "Standard", 25, 5),
            row("Central", "B", "b", "First", 75, 0),
        ]
        result = analyze(rows)
        self.assertTrue(isclose(result["gap_pp"], -5))
        self.assertTrue(isclose(result["product_effects_pp"]["category_mix"], -5))
        self.assertTrue(isclose(result["product_effects_pp"]["subcategory_mix"], 0, abs_tol=1e-12))
        self.assertTrue(isclose(result["product_effects_pp"]["within_product_margin"], 0, abs_tol=1e-12))
        self.assertTrue(isclose(sum(result["shipping_effects_pp"].values()), -5))

    def test_within_product_margin_when_shares_match(self):
        rows = [
            row("West", "A", "a", "Standard", 50, 10),
            row("West", "A", "b", "First", 50, 5),
            row("Central", "A", "a", "Standard", 50, 0),
            row("Central", "A", "b", "First", 50, 5),
        ]
        result = analyze(rows)
        self.assertTrue(isclose(result["gap_pp"], -10))
        self.assertTrue(isclose(result["product_effects_pp"]["within_product_margin"], -10))
        self.assertTrue(isclose(sum(result["product_effects_pp"].values()), -10))

    def test_pure_subcategory_mix(self):
        rows = [
            row("West", "A", "a", "Standard", 50, 10),
            row("West", "A", "b", "Standard", 50, 0),
            row("Central", "A", "a", "Standard", 25, 5),
            row("Central", "A", "b", "Standard", 75, 0),
        ]
        result = analyze(rows)
        self.assertTrue(isclose(result["product_effects_pp"]["subcategory_mix"], -5))
        self.assertTrue(isclose(result["product_effects_pp"]["category_mix"], 0, abs_tol=1e-12))
        self.assertTrue(isclose(result["product_effects_pp"]["within_product_margin"], 0, abs_tol=1e-12))

    def test_missing_shared_product_is_not_imputed(self):
        rows = [row("West", "A", "a", "Standard", 100, 10),
                row("Central", "B", "b", "Standard", 100, 5)]
        with self.assertRaisesRegex(ValueError, "shared positive-sales"):
            analyze(rows)

    def test_invalid_sales_is_rejected(self):
        rows = [row("West", "A", "a", "Standard", 100, 10),
                row("Central", "A", "a", "Standard", 0, 5)]
        with self.assertRaisesRegex(ValueError, "Invalid sales"):
            analyze(rows)

    def test_committed_source_reconciles_both_alternative_views(self):
        with (ROOT / "data" / "Sample - Superstore.csv").open(newline="", encoding="latin1") as handle:
            result = analyze(list(csv.DictReader(handle)))
        self.assertTrue(isclose(result["gap_pp"], 7.921628591177565 - 14.944831420727203, abs_tol=1e-9))
        for factors in ("product_effects_pp", "shipping_effects_pp"):
            self.assertTrue(isclose(sum(result[factors].values()), result["gap_pp"], abs_tol=1e-9))
        self.assertEqual(len(result["discount_rows"]), 36)


if __name__ == "__main__":
    unittest.main()
