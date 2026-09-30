"""Independent examples for purchase grain, censoring and SQL windows."""

import csv
from pathlib import Path
import sqlite3
import tempfile
import unittest

from sql.run_analysis import ROOT, build_database, run_query


FIELDS = ["Row ID", "Order ID", "Customer ID", "Order Date", "Region", "Segment",
          "Sales", "Profit", "Quantity", "Discount"]


def purchase(row_id, order_id, customer_id, day, sales="10", region="West"):
    return dict(zip(FIELDS, [row_id, order_id, customer_id, day, region, "Consumer",
                            sales, "1.2345", "1", "0"]))


class CustomerSQLTests(unittest.TestCase):
    def database(self, rows, cutoff=None):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        source = Path(directory.name) / "source.csv"
        with source.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        connection = build_database(source, cutoff)
        self.addCleanup(connection.close)
        return connection

    def test_lines_do_not_become_repeat_purchases_and_money_is_exact(self):
        connection = self.database([
            purchase(1, "A", "C1", "1/1/2020", "0.1"),
            purchase(2, "A", "C1", "1/1/2020", "0.2"),
            purchase(3, "B", "C1", "4/1/2020"),
        ])
        totals = run_query(connection, "01_reconciliation.sql")[0]
        self.assertEqual((totals["orders"], totals["order_lines"], totals["sales_micros"]),
                         (2, 3, 10_300_000))
        sequence = connection.execute(
            "SELECT purchase_number, cumulative_sales_micros FROM customer_order_sequence "
            "ORDER BY purchase_number"
        ).fetchall()
        self.assertEqual([tuple(r) for r in sequence], [(1, 300000), (2, 10300000)])

    def test_zero_activity_is_zero_and_future_cohort_month_is_null(self):
        connection = self.database([
            purchase(1, "A", "C1", "1/1/2020"),
            purchase(2, "B", "C2", "3/31/2020"),
        ])
        january = [r for r in run_query(connection, "03_monthly_cohort_retention.sql")
                   if r["cohort_month"] == "2020-01-01"]
        self.assertEqual(january[0]["retention_rate"], 1)
        self.assertEqual(january[1]["retention_rate"], 0)
        self.assertEqual(january[3]["observable"], 0)
        self.assertIsNone(january[3]["active_customers"])
        self.assertIsNone(january[3]["retention_rate"])

    def test_repeat_boundary_censored_customer_and_stable_first_region(self):
        connection = self.database([
            purchase(1, "A", "C1", "1/1/2020"),
            purchase(2, "B", "C1", "3/31/2020", region="East"),  # Exactly 90 days.
            purchase(3, "C", "C2", "3/20/2020"),
            purchase(4, "D", "C2", "3/21/2020"),  # Repeat but not fully observed.
        ])
        rows = run_query(connection, "04_repeat_purchase_90d.sql")
        total = next(r for r in rows if r["breakdown"] == "all")
        self.assertEqual((total["eligible_customers"], total["repeat_customers"],
                          total["censored_customers"]), (1, 1, 1))
        self.assertEqual(total["repeat_rate_90d"], 1)
        self.assertFalse(any(r["segment_value"] == "East" for r in rows))

    def test_partial_month_is_unobservable_and_zero_eligible_is_null(self):
        connection = self.database([purchase(1, "A", "C1", "1/30/2020")])
        cohort = run_query(connection, "03_monthly_cohort_retention.sql")[0]
        repeat = run_query(connection, "04_repeat_purchase_90d.sql")[0]
        self.assertEqual(cohort["observable"], 0)
        self.assertIsNone(cohort["retention_rate"])
        self.assertIsNone(repeat["repeat_rate_90d"])

    def test_cutoff_excludes_future_orders(self):
        connection = self.database([
            purchase(1, "A", "C1", "1/1/2020"),
            purchase(2, "B", "C1", "4/1/2020"),
        ], "2020-03-31")
        lifecycle = run_query(connection, "02_customer_lifecycle.sql")[0]
        self.assertEqual(lifecycle["orders"], 1)
        self.assertIsNone(lifecycle["second_order_date"])

    def test_month_spine_and_calendar_lag(self):
        connection = self.database([
            purchase(1, "A", "C1", "1/1/2020"),
            purchase(2, "B", "C1", "3/31/2020", "20"),
        ])
        months = run_query(connection, "05_monthly_customer_revenue.sql")
        self.assertEqual([r["sales"] for r in months], [10, 0, 20])
        self.assertEqual(months[2]["previous_month_sales"], 0)
        self.assertIsNone(months[2]["sales_change_vs_previous_month"])
        self.assertEqual(months[2]["rolling_3m_sales"], 30)
        self.assertEqual(months[2]["repeat_order_sales"], 20)

    def test_same_day_distinct_orders_have_deterministic_sequence(self):
        connection = self.database([
            purchase(1, "B", "C1", "1/1/2020"),
            purchase(2, "A", "C1", "1/1/2020"),
            purchase(3, "C", "C2", "4/1/2020"),
        ])
        sequence = connection.execute(
            "SELECT order_id, purchase_number, previous_order_date "
            "FROM customer_order_sequence WHERE customer_id = 'C1' ORDER BY purchase_number"
        ).fetchall()
        self.assertEqual([tuple(r) for r in sequence], [("A", 1, None), ("B", 2, "2020-01-01")])

    def test_inconsistent_order_and_duplicate_line_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Inconsistent order"):
            self.database([purchase(1, "A", "C1", "1/1/2020"),
                           purchase(2, "A", "C2", "1/1/2020")])
        with self.assertRaises(sqlite3.IntegrityError):
            self.database([purchase(1, "A", "C1", "1/1/2020"),
                           purchase(1, "A", "C1", "1/1/2020")])

    def test_revenue_ranking_ties_and_cumulative_share(self):
        connection = self.database([
            purchase(1, "A", "C1", "1/1/2020", "30"),
            purchase(2, "B", "C2", "1/1/2020", "20"),
            purchase(3, "C", "C3", "1/1/2020", "20"),
            purchase(4, "D", "C4", "1/1/2020", "10"),
        ])
        rows = run_query(connection, "06_customer_revenue_concentration.sql")
        self.assertEqual([r["sales_rank"] for r in rows], [1, 2, 2, 3])
        self.assertEqual(rows[0]["cumulative_sales_share"], 0.375)
        self.assertEqual(rows[-1]["cumulative_sales_share"], 1)

    def test_committed_source_reconciles_and_cohorts_partition_customers(self):
        connection = build_database(ROOT / "data" / "Sample - Superstore.csv")
        self.addCleanup(connection.close)
        totals = run_query(connection, "01_reconciliation.sql")[0]
        self.assertEqual((totals["order_lines"], totals["orders"], totals["customers"]),
                         (9994, 5009, 793))
        self.assertEqual(totals["sales_micros"], 2297200860300)
        cohort_rows = run_query(connection, "03_monthly_cohort_retention.sql")
        self.assertEqual(sum(r["cohort_customers"] for r in cohort_rows if r["age_months"] == 0), 793)
        for r in cohort_rows:
            if r["observable"]:
                self.assertLessEqual(r["active_customers"], r["cohort_customers"])
                if r["age_months"] == 0:
                    self.assertEqual(r["retention_rate"], 1)


if __name__ == "__main__":
    unittest.main()
