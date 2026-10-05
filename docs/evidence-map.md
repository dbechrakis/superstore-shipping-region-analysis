# Current evidence and historical deliverables

| Material | Status | How to use it |
|---|---|---|
| `analysis/`, `scripts/build_margin_drivers.py`, `outputs/margin_drivers.json` and related tables | Current, executable | Reconciled product/shipping decompositions; run the script and evidence checks |
| `sql/`, `outputs/sql/` | Current, executable | Order/customer grain, first-observed cohorts and censored repeat-purchase measures |
| `demo/` | Current interactive companion | Static aggregate profitability explorer; deployed to GitHub Pages from this repo |
| `notebooks/Superstore_Shipping_Regional_Analysis.ipynb`, regional/dispatch exports | Executed analytical companion | Regional totals and dispatch metrics documented in the README |
| `dashboard/Superstore_Sales.pbix` | Historical group deliverable | Inspect original Power BI work; current claims must reconcile to the executable evidence |
| `docs/Superstore_Sales_Report.docx` | Historical group deliverable | Retained with team credit; embedded wording/results were not refreshed |
| `docs/shipping_region_analysis.html` | Historical group dashboard, recalculated | Figures recalculated from the committed CSV on 2026-10-05 and checked by `tests/test_archived_dashboard.py` |

Small source CSVs and inspectable result tables are retained intentionally for reproduction. The historical PBIX/Office files preserve original work rather than acting as the current analytical reference. Model binaries or service dependencies are not required for the new SQL case.

The main profile showcases four maintained projects. AAPL and World Bank remain available as earlier studies and are not part of that README showcase.
