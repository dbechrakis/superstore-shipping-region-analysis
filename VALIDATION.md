# Validation record

Review date: 2026-09-05 (UTC).

Executed the complete revised Python notebook against the committed CSV; archived PBIX and office deliverables were not rerendered.

Changes were prepared with AI assistance and should be understood and reviewed by the repository owner. Historical records are not labelled as freshly reproduced results.

## Margin-driver companion — 2026-09-25 (UTC)

The source remains the committed 9,994-line CSV (SHA-256 `58fb59c63089e564d835e4aabe19d371757de1137a5bf1888243ae386c4b7a97`). `python -m scripts.build_margin_drivers` generated the new output JSON and CSVs. The category/product Shapley view reconciles +0.273 +0.451 −7.747 = −7.023 pp at three decimals; the alternative shipping-mode view also reconciles. `python ci/verify_evidence.py` recomputes all cells from source and validates the published outputs. `python -m unittest discover -s tests -v` exercises synthetic invariants and the full dataset.

The historical notebook, PBIX, DOCX, HTML dashboard and live explorer were not rewritten or republished. The new decomposition applies to the full 2014–2017 Central–West comparison, not to arbitrary interactive filter selections. It describes accounting composition, not causal effects or a profit forecast.
