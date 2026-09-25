# Margin-driver investigation

## Question and source

Why is Central's recorded profit margin lower than West's in the full 2014–2017 Sample Superstore extract? The comparison uses transaction lines, `Sales` and `Profit`, from the committed `data/Sample - Superstore.csv` (SHA-256 in `outputs/margin_drivers.json`). Margin is **sum of profit / sum of realized sales**; the unit of the decomposition is percentage points (pp), not dollars or order counts. The observed 7.02 pp gap is Central minus West.

The same 3 categories, 17 category/subcategory cells, and 4 shipping modes have positive sales in both regions. The script refuses to impute an unobserved cell if that condition fails.

## Exact product decomposition

Within each region, margin is the sum over categories and subcategories of

`category sales share × subcategory share within category × subcategory profit/sales`.

The three factors are category mix, within-category subcategory mix, and within-subcategory margin. For each of their six possible change orders, the script starts with West's factors, substitutes Central's factors one at a time, and records each factor's marginal effect. Averaging over orders (a Shapley accounting allocation) assigns interaction terms symmetrically. The three contributions reconcile to Central minus West to numerical precision; no residual category is needed.

| Factor | Central − West (pp) | Reading |
|---|---:|---|
| Category sales mix | +0.273 | Slightly offsets the gap |
| Product mix *within* categories | +0.451 | Also offsets the gap |
| Within-product recorded margin | −7.747 | Dominant negative component |
| **Observed margin gap** | **−7.023** | **7.92% versus 14.94%** |

The displayed components reconcile at three decimals; exact values are in the output JSON. The largest negative within-product contributions to the **overall regional margin difference** are Binders (−2.91 pp), Furnishings (−1.83 pp), Appliances (−1.71 pp), and Tables (−1.05 pp). These are not the same as ranking subcategories by raw profit loss: a product can be profitable in Central yet contribute negatively if its margin is much lower than West's. Phones (+1.09 pp) partly offsets the deficits. See the signed contributions for every cell in [`product_margin_contributions.csv`](../outputs/product_margin_contributions.csv).

## Discount and shipping checks

The recorded line-level discount is not an independently additive fourth component of the product decomposition. In this extract, lines with a discount **at least 30%** represent **25.76% of Central's realized sales**, versus **2.35% of West's**. The sales-weighted discount is 15.52% versus 12.88%. The distinction matters: line frequency, realized-sales weighting, product mix and discount depth are different quantities. The accompanying [`discount_diagnostic.csv`](../outputs/discount_diagnostic.csv) shows both by subcategory. A high-discount line may coexist with a loss, but this does not identify the causal impact of removing the discount; margin also reflects product/price/cost differences and selection.

Shipping mode is a **separate alternative partition of the same 7.02 pp gap**, not an extra component to add to the product result. In a two-factor Shapley decomposition over shipping-mode sales shares and within-mode margins, shipping-mode mix is −0.11 pp and within-mode recorded margin is −6.91 pp. The latter contains commercial/product effects too; it is **not** a shipping-cost estimate. The source has dispatch dates but neither delivery dates nor an isolated logistics-cost breakdown. See [`shipping_mode_contributions.csv`](../outputs/shipping_mode_contributions.csv).

## Decision use and limits

Prioritize a review of pricing, discounts, product economics and recorded cost for Binders, Furnishings, Appliances and Tables. Check transaction-level composition and cost accounting before proposing a change. Then test a specific intervention prospectively: the historical gap and Shapley allocation are descriptive accounting identities, not forecasts of profit uplift or causal attributions. No comparison here controls for customers, geography within regions, seasonality, or all cost components.

To regenerate the three CSVs and JSON from the included source, run `python -m scripts.build_margin_drivers` at the repository root (Python 3.12, standard library only). Use `--focus` and `--reference` for another pair of regions. `python ci/verify_evidence.py` independently recomputes and checks every committed contribution and diagnostic row; `python -m unittest discover -s tests -v` checks decomposition invariants. The original notebook, Power BI and office files are preserved and have not been silently rewritten with these results.
