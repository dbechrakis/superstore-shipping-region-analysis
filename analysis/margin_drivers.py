"""Exact accounting decompositions of regional sales-weighted profit margin.

These are descriptive decompositions, not estimates of intervention effects.
The product and shipping views are alternative partitions of the *same* gap;
their components must not be added to each other.
"""

from collections import defaultdict
from itertools import permutations
from math import factorial
from math import isclose, isfinite


PRODUCT_FACTORS = ("category_mix", "subcategory_mix", "within_product_margin")
SHIPPING_FACTORS = ("shipping_mode_mix", "within_mode_margin")


def _aggregate(rows, keys):
    grouped = defaultdict(lambda: {"sales": 0.0, "profit": 0.0, "lines": 0,
                                  "discount_sales": 0.0, "high_discount_sales": 0.0})
    for row in rows:
        key = tuple(row[field] for field in keys)
        sales, profit, discount = (float(row[field]) for field in ("Sales", "Profit", "Discount"))
        if not all(map(isfinite, (sales, profit, discount))) or sales <= 0 or not 0 <= discount <= 1:
            raise ValueError(f"Invalid sales, profit or discount on Row ID {row['Row ID']}")
        bucket = grouped[key]
        bucket["sales"] += sales
        bucket["profit"] += profit
        bucket["lines"] += 1
        bucket["discount_sales"] += sales * discount
        if discount >= 0.30:
            bucket["high_discount_sales"] += sales
    return grouped


def _shapley(factors, keys, value):
    """Allocate an exact difference symmetrically over all factor orderings."""
    result = {factor: {key: 0.0 for key in keys} for factor in factors}
    for ordering in permutations(factors):
        selected = set()
        before = {key: value(key, selected) for key in keys}
        for factor in ordering:
            selected.add(factor)
            after = {key: value(key, selected) for key in keys}
            for key in keys:
                result[factor][key] += (after[key] - before[key]) / factorial(len(factors))
            before = after
    return result


def analyze(rows, focus="Central", reference="West"):
    """Compare two regions, returning percentage-point contributions and QA.

    Categories, their subcategories, and shipping modes must have positive
    sales in both regions. No missing-cell margin is fabricated or imputed.
    """
    if focus == reference:
        raise ValueError("Focus and reference must be different regions")
    selected = [r for r in rows if r["Region"] in (focus, reference)]
    if {r["Region"] for r in selected} != {focus, reference}:
        raise ValueError("Both requested regions must be present")

    leaves = _aggregate(selected, ("Region", "Category", "Sub-Category"))
    modes = _aggregate(selected, ("Region", "Ship Mode"))
    totals = _aggregate(selected, ("Region",))
    categories = sorted({category for _, category, _ in leaves})
    products = sorted({(category, subcategory) for _, category, subcategory in leaves})
    ship_modes = sorted({mode for _, mode in modes})
    for region in (reference, focus):
        if any((region, *key) not in leaves for key in products):
            raise ValueError("Product decomposition requires shared positive-sales product cells")
        if any((region, mode) not in modes for mode in ship_modes):
            raise ValueError("Shipping decomposition requires shared positive-sales modes")

    category_sales = defaultdict(float)
    for (region, category, _), item in leaves.items():
        category_sales[region, category] += item["sales"]

    def product_value(key, chosen):
        category, subcategory = key
        category_region = focus if "category_mix" in chosen else reference
        product_region = focus if "subcategory_mix" in chosen else reference
        margin_region = focus if "within_product_margin" in chosen else reference
        category_share = category_sales[category_region, category] / totals[(category_region,)]["sales"]
        product_share = leaves[product_region, category, subcategory]["sales"] / category_sales[product_region, category]
        item = leaves[margin_region, category, subcategory]
        return 100 * category_share * product_share * item["profit"] / item["sales"]

    product_parts = _shapley(PRODUCT_FACTORS, products, product_value)
    product_rows = [
        {"category": category, "subcategory": subcategory, "factor": factor,
         "contribution_pp": product_parts[factor][(category, subcategory)]}
        for factor in PRODUCT_FACTORS for category, subcategory in products
    ]

    def mode_value(mode, chosen):
        share_region = focus if "shipping_mode_mix" in chosen else reference
        margin_region = focus if "within_mode_margin" in chosen else reference
        share = modes[share_region, mode]["sales"] / totals[(share_region,)]["sales"]
        item = modes[margin_region, mode]
        return 100 * share * item["profit"] / item["sales"]

    mode_parts = _shapley(SHIPPING_FACTORS, ship_modes, mode_value)
    shipping_rows = [
        {"ship_mode": mode, "factor": factor, "contribution_pp": mode_parts[factor][mode]}
        for factor in SHIPPING_FACTORS for mode in ship_modes
    ]

    margin = {region: 100 * totals[(region,)]["profit"] / totals[(region,)]["sales"]
              for region in (reference, focus)}
    gap = margin[focus] - margin[reference]
    product_effects = {f: sum(product_parts[f].values()) for f in PRODUCT_FACTORS}
    shipping_effects = {f: sum(mode_parts[f].values()) for f in SHIPPING_FACTORS}
    if not isclose(sum(product_effects.values()), gap, abs_tol=1e-10) or not isclose(
            sum(shipping_effects.values()), gap, abs_tol=1e-10):
        raise AssertionError("The accounting decomposition does not reconcile")

    discount_rows = []
    for region in (focus, reference):
        for key in [(region,)] + [(region, *product) for product in products]:
            item = totals[key] if len(key) == 1 else leaves[key]
            discount_rows.append({
                "region": region,
                "category": key[1] if len(key) > 1 else "ALL",
                "subcategory": key[2] if len(key) > 1 else "ALL",
                "sales": item["sales"], "profit": item["profit"],
                "margin_pct": 100 * item["profit"] / item["sales"],
                "lines": item["lines"],
                "sales_weighted_discount_pct": 100 * item["discount_sales"] / item["sales"],
                "sales_share_discount_ge_30_pct": 100 * item["high_discount_sales"] / item["sales"],
            })
    return {
        "focus": focus, "reference": reference, "margins_pct": margin, "gap_pp": gap,
        "product_effects_pp": product_effects, "product_rows": product_rows,
        "shipping_effects_pp": shipping_effects, "shipping_rows": shipping_rows,
        "discount_rows": discount_rows,
        "reconciliation_residual_pp": gap - sum(product_effects.values()),
        "shipping_reconciliation_residual_pp": gap - sum(shipping_effects.values()),
    }
