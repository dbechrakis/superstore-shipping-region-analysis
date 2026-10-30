import csv
from pathlib import Path
import unittest

from analysis.discount_bands import band_of, band_table, trimming_table

SOURCE = Path(__file__).resolve().parents[1] / "data" / "Sample - Superstore.csv"


def line(region, sales, profit, discount):
    return {"Region": region, "Sales": str(sales), "Profit": str(profit), "Discount": str(discount)}


class BandEdgeTests(unittest.TestCase):
    def test_edges_go_to_the_higher_band(self):
        self.assertEqual([band_of(d) for d in (0, 0.0001, 0.29, 0.30, 0.49, 0.50, 1.0)],
                         ["no_discount", "under_30_pct", "under_30_pct", "30_to_49_pct", "30_to_49_pct",
                          "50_pct_or_more", "50_pct_or_more"])

    def test_a_discount_outside_zero_to_one_is_rejected(self):
        for value in (-0.1, 1.01):
            with self.subTest(value=value), self.assertRaises(ValueError):
                band_of(value)


class BandTableTests(unittest.TestCase):
    rows = [line("A", 100, 30, 0), line("A", 100, -20, 0.4), line("A", 50, -10, 0.6),
            line("B", 200, 60, 0), line("B", 50, 5, 0.1)]

    def test_bands_add_up_to_each_regions_margin_and_the_differences_to_the_gap(self):
        table, gap = band_table(self.rows, "A", "B")
        for region, profit, sales in (("A", 0, 250), ("B", 65, 250)):
            contributions = sum(r["contribution_to_margin_pp"] for r in table if r["region"] == region)
            expected = 100 * sum(float(x["Profit"]) for x in self.rows if x["Region"] == region) / \
                sum(float(x["Sales"]) for x in self.rows if x["Region"] == region)
            self.assertAlmostEqual(contributions, expected)
        self.assertAlmostEqual(gap, 0 - 26.0)

    def test_an_empty_band_has_no_margin_instead_of_a_made_up_one(self):
        table, _ = band_table(self.rows, "A", "B")
        empty = next(r for r in table if r["region"] == "B" and r["discount_band"] == "30_to_49_pct")
        self.assertEqual((empty["lines"], empty["sales"], empty["margin_pct"]), (0, 0.0, ""))

    def test_an_unknown_region_is_rejected(self):
        with self.assertRaises(ValueError):
            band_table(self.rows, "A", "Z")


class TrimmingTests(unittest.TestCase):
    def test_zero_trim_equals_the_gap_and_trimming_removes_the_worst_lines(self):
        rows = [line("A", 100, 20, 0), line("A", 100, -80, 0.8), line("B", 100, 20, 0), line("B", 100, 10, 0)]
        result = trimming_table(rows, "A", "B", counts=(0, 1))
        self.assertAlmostEqual(result[0]["gap_pp"], -45.0)
        self.assertAlmostEqual(result[1]["a_margin_pct"], 20.0)
        self.assertAlmostEqual(result[1]["b_margin_pct"], 20.0)


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SOURCE.open(newline="", encoding="latin1") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_the_central_gap_sits_in_the_discounted_bands(self):
        table, gap = band_table(self.rows)
        by_key = {(r["region"], r["discount_band"]): r for r in table}
        self.assertAlmostEqual(gap, -7.0232, places=3)
        self.assertEqual(by_key["West", "30_to_49_pct"]["lines"], 0)
        self.assertGreater(by_key["Central", "no_discount"]["margin_pct"], by_key["West", "no_discount"]["margin_pct"])
        self.assertLess(by_key["Central", "30_to_49_pct"]["margin_pct"], 0)

    def test_trimming_the_worst_lines_shrinks_the_gap(self):
        gaps = [r["gap_pp"] for r in trimming_table(self.rows)]
        self.assertTrue(all(later > earlier for earlier, later in zip(gaps, gaps[1:])))
        self.assertGreater(gaps[-1], -1.0)


if __name__ == "__main__":
    unittest.main()
