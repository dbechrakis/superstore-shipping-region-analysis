"""Where the regional margin gap sits across discount levels.

Everything here is accounting on the recorded lines. It does not estimate what a different discount
would have done, and it cannot: one region has no sales in a whole discount band.
"""

from collections import defaultdict
from math import isclose

BANDS = (
    ("no_discount", lambda d: d == 0),
    ("under_30_pct", lambda d: 0 < d < 0.30),
    ("30_to_49_pct", lambda d: 0.30 <= d < 0.50),
    ("50_pct_or_more", lambda d: d >= 0.50),
)
TRIM_COUNTS = (0, 5, 10, 25, 50, 100)


def band_of(discount):
    if not 0 <= discount <= 1:
        raise ValueError(f"Discount {discount} is outside 0 to 1")
    for name, test in BANDS:
        if test(discount):
            return name
    raise ValueError(f"Discount {discount} is outside 0 to 1")


def _region_rows(rows, region):
    chosen = [r for r in rows if r["Region"] == region]
    if not chosen:
        raise ValueError(f"No rows for region {region}")
    return [(float(r["Sales"]), float(r["Profit"]), float(r["Discount"])) for r in chosen]


def _margin(lines):
    sales = sum(s for s, _, _ in lines)
    return 100 * sum(p for _, p, _ in lines) / sales


def band_table(rows, focus="Central", reference="West"):
    """Per region and discount band: sales share, margin and contribution to the region's margin.

    Contribution is band profit over the region's total sales, in percentage points, so the four
    bands add up to the region's margin and the band differences add up to the gap.
    """
    table = []
    totals = {}
    for region in (focus, reference):
        lines = _region_rows(rows, region)
        total_sales = sum(s for s, _, _ in lines)
        totals[region] = 100 * sum(p for _, p, _ in lines) / total_sales
        grouped = defaultdict(lambda: [0.0, 0.0, 0])
        for sales, profit, discount in lines:
            bucket = grouped[band_of(discount)]
            bucket[0] += sales
            bucket[1] += profit
            bucket[2] += 1
        for name, _ in BANDS:
            sales, profit, count = grouped.get(name, [0.0, 0.0, 0])
            table.append({
                "region": region, "discount_band": name, "lines": count, "sales": sales, "profit": profit,
                "sales_share_pct": 100 * sales / total_sales,
                "margin_pct": 100 * profit / sales if sales else "",
                "contribution_to_margin_pp": 100 * profit / total_sales,
            })
    gap = totals[focus] - totals[reference]
    contributions = {(r["region"], r["discount_band"]): r["contribution_to_margin_pp"] for r in table}
    difference = sum(contributions[focus, name] - contributions[reference, name] for name, _ in BANDS)
    if not isclose(difference, gap, abs_tol=1e-9):
        raise AssertionError("Discount bands do not reconcile to the margin gap")
    return table, gap


def trimming_table(rows, focus="Central", reference="West", counts=TRIM_COUNTS):
    """Margin gap after removing the k lowest-profit lines from each region.

    Trimming both regions by the same count keeps the comparison fair. It shows how few lines carry
    the gap. It is not a recommendation to drop lines.
    """
    lines = {region: sorted(_region_rows(rows, region), key=lambda line: line[1]) for region in (focus, reference)}
    result = []
    for k in counts:
        margins = {region: _margin(lines[region][k:]) for region in (focus, reference)}
        result.append({
            "lines_removed_per_region": k,
            "share_of_focus_lines_pct": 100 * k / len(lines[focus]),
            f"{focus.lower()}_margin_pct": margins[focus],
            f"{reference.lower()}_margin_pct": margins[reference],
            "gap_pp": margins[focus] - margins[reference],
        })
    return result


def _r_squared(values, keys):
    mean = sum(values) / len(values)
    total = sum((v - mean) ** 2 for v in values)
    groups = defaultdict(list)
    for v, k in zip(values, keys):
        groups[k].append(v)
    cell_mean = {k: sum(g) / len(g) for k, g in groups.items()}
    within = sum((v - cell_mean[k]) ** 2 for v, k in zip(values, keys))
    return 1 - within / total


def discount_determinism(rows):
    """How much of each line's margin (profit over sales) the recorded discount fixes.

    Each line is predicted by the mean margin of its cell, and the share of variance explained is
    reported for sub-category alone, discount alone and the two together. In real transactions price,
    cost and customer would leave much of the margin unexplained. A share near one means the extract's
    profit is close to a fixed function of discount within a product, which is how Sample Superstore,
    a demonstration dataset, behaves.
    """
    lines = [r for r in rows if float(r["Sales"]) > 0]
    margin = [float(r["Profit"]) / float(r["Sales"]) for r in lines]
    sub = [r["Sub-Category"] for r in lines]
    disc = [round(float(r["Discount"]), 4) for r in lines]
    return {
        "lines": len(lines),
        "r2_subcategory": _r_squared(margin, sub),
        "r2_discount": _r_squared(margin, disc),
        "r2_subcategory_x_discount": _r_squared(margin, list(zip(sub, disc))),
        "cells_subcategory_x_discount": len(set(zip(sub, disc))),
    }
