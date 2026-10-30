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
