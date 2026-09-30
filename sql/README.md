# SQL customer lifecycle case

**Question:** where should a repeat-purchase investigation start, after giving customers comparable time to return?

This case runs directly over the same committed Superstore CSV as the profitability study. SQLite is used to make the queries executable with Python's standard library. The SQL uses CTEs, a recursive date spine, joins, conditional aggregation, `ROW_NUMBER`, `LAG`, `LEAD`, `DENSE_RANK`, `NTILE` and explicit window frames.

## Reproduce

```bash
python -m sql.run_analysis
python -m unittest discover -s tests -v
python ci/verify_evidence.py
```

No service, credentials or generated database download is needed. The loader uses an in-memory database; calculations live in the `.sql` files. To inspect an earlier snapshot, use `python -m sql.run_analysis --as-of 2016-12-31 --output /tmp/superstore-2016`.

## Grain and contracts

| Layer | Grain | Contract |
|---|---|---|
| `order_lines` | Source Row ID | Unique, required IDs, parsed US dates, positive sales/quantity, valid discount |
| `orders` | Order ID | One customer/date/region/segment per order; line amounts reconciled exactly |
| `customer_order_sequence` | Customer × order | Stable ordering by date then Order ID; full history only up to `as_of` |
| Cohort output | First-observed month × age | One cohort membership per customer; distinct active customers |

Source monetary amounts are stored as integer millionths, preserving their sub-cent precision. Exported floating ratios are formatted to 12 significant digits. Source line and order totals reconcile before outputs are accepted. Customer names and addresses are not loaded into the SQL layer.

## Queries

| Query | Business purpose | SQL concepts |
|---|---|---|
| [01](queries/01_reconciliation.sql) | Prove order/customer counts and amounts reconcile | Aggregation, distinct counts |
| [02](queries/02_customer_lifecycle.sql) | Identify first/second purchases and current recency | Conditional aggregation over windowed order history |
| [03](queries/03_monthly_cohort_retention.sql) | Compare activity at the same cohort age | Recursive age grid, left join, censoring |
| [04](queries/04_repeat_purchase_90d.sql) | Compare repeat purchase within equal 90-day windows | Eligibility, conditional counts, `NULLIF` |
| [05](queries/05_monthly_customer_revenue.sql) | Separate first/repeat-order sales and calendar trends | Date spine, `LAG`, rolling `ROWS` frame |
| [06](queries/06_customer_revenue_concentration.sql) | Assess revenue concentration and inspect profit alongside sales | `DENSE_RANK`, `NTILE`, cumulative share |

## Current evidence and decision

The source contains **9,994 lines, 5,009 orders and 793 observed customers**. Within a fully observed 90-day window, **181 of 790 eligible customers** placed a second distinct order: **22.91%**. Three customers are censored and excluded from that denominator.

| First-order region | Eligible customers | Repeat customers | 90-day repeat rate |
|---|---:|---:|---:|
| Central | 196 | 49 | 25.00% |
| East | 203 | 51 | 25.12% |
| South | 139 | 27 | 19.42% |
| West | 252 | 54 | 21.43% |

**Next investigation:** inspect the South cohort mix, seasonality and sample coverage before proposing a retention intervention. These descriptive differences do not demonstrate a regional effect or a profitable campaign. The highest-sales customer also has negative recorded profit, so a sales-only targeting rule would need an economics check.

The [committed exports](../outputs/sql) and [manifest](../outputs/sql/manifest.json) record source/query hashes and the analysis cutoff. CI regenerates the CSVs and checks them against the committed evidence.

## Interpretation boundaries

- First observed purchase is **not verified acquisition**. Purchases before the snapshot are unknown; initial cohorts may include existing customers.
- Retention means **activity in a specified calendar month**, not cumulative survival or absence of churn. It need not decrease monotonically.
- A month is observable only when its entire calendar window lies between the first observed source date and the cutoff. Unobservable cells are `NULL`; observable cells with no activity are zero. The source spans 2014-01-03 to 2017-12-30, so boundary months are conservatively excluded from full-month measures.
- Ninety-day repeat purchase uses a second distinct Order ID. Same-day distinct orders count as repeats; date ties use Order ID because no order timestamps are available.
- First-order region/segment remain fixed for the repeat comparison. Switching location later does not reassign the original cohort.
- Superstore is a sample snapshot. No recorded purchase does not prove inactivity in the full business. Full-window observed sales are not predicted lifetime value.
- No sessions, visitors or randomized assignments are supplied. This case does not fabricate a conversion funnel or an A/B test.

## Interview exercise

Write an additional query returning first-order regions with at least 100 eligible customers, ranked by their 90-day repeat rate. Use a CTE and `DENSE_RANK`; keep the denominator restricted to full 90-day windows. Explain why removing the eligibility condition changes the question. Keep your query separate until it has been reviewed against query 04.
