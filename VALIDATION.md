# Validation record

Review date: 2026-09-05 (UTC).

Executed the complete revised Python notebook against the committed CSV; archived PBIX and office deliverables were not rerendered.

Changes were prepared with AI assistance and should be understood and reviewed by the repository owner. Historical records are not labelled as freshly reproduced results.

## Margin-driver companion — 2026-09-25 (UTC)

The source remains the committed 9,994-line CSV (SHA-256 `58fb59c63089e564d835e4aabe19d371757de1137a5bf1888243ae386c4b7a97`). `python -m scripts.build_margin_drivers` generated the new output JSON and CSVs. The category/product Shapley view reconciles +0.273 +0.451 −7.747 = −7.023 pp at three decimals; the alternative shipping-mode view also reconciles. `python ci/verify_evidence.py` recomputes all cells from source and validates the published outputs. `python -m unittest discover -s tests -v` exercises synthetic invariants and the full dataset.

The historical notebook, PBIX, DOCX, HTML dashboard and live explorer were not rewritten or republished. The new decomposition applies to the full 2014–2017 Central–West comparison, not to arbitrary interactive filter selections. It describes accounting composition, not causal effects or a profit forecast.
# SQL customer evidence — September 30, 2026

Executed all six queries on the committed source with Python 3.12. The order/customer layer reconciles 9,994 source lines to 5,009 orders and 793 customers without join inflation. Monetary source totals preserve sub-cent precision: sales 2,297,200.8603 and profit 286,397.0217. The new lifecycle outputs identify 181 repeat purchasers among 790 customers with complete 90-day follow-up; three customers are censored. Monthly boundary periods outside the observed span are NULL rather than zero.

Ten new SQL tests cover multi-line order grain, exact amounts, zero activity, censoring, the inclusive 90-day boundary, first-order dimensions, date cutoffs, empty calendar months, same-day ordering, duplicate/inconsistent records and source reconciliation. Existing margin tests also pass. CI regenerates the SQL exports and compares source/query hashes and committed tables. These are descriptive sample-data results, not measured retention intervention effects.
