# Superstore — Shipping & Regional Analysis

Business intelligence analysis of the **Sample Superstore** retail dataset, combining Python analysis, Power BI modeling, and a lightweight interactive HTML dashboard. The project focuses on regional profitability, shipping-mode performance, delivery time, and late shipments.

> **Context:** Group project for Data Visualization (ITC6004A1), Deree – The American College of Greece, Winter Term 2026.

## Business questions

- Which regions generate revenue efficiently, and where is margin leaking?
- Does shipping-mode mix differ materially by region?
- Are delivery times consistent across regions and shipping modes?
- Where are late Standard Class shipments concentrated?
- What operational vs. commercial explanations are supported by the data?

## Key findings

- Revenue reached approximately **$2.30M** with **$286.40K** total profit and a **12.47%** overall margin in the supplied Power BI analysis.
- **Central** is the main regional profitability issue: approximately **$501K sales at 7.92% margin**, versus **14.94% in West**.
- **Standard Class** is the dominant shipping mode across all four regions.
- Average shipping time is highly similar across regions; Standard Class is roughly **five days** in each region.
- The supplied analysis therefore points more strongly toward **pricing/discount policy** than logistics as the explanation for Central's margin gap.
- The report also identifies **Furniture**, especially Tables and Bookcases, and deep discounting as major sources of margin pressure.

These findings are documented in the supplied project report and Power BI dashboard. The Python notebook reproduces the core shipping/regional calculations from the CSV.

## Deliverables

| Artifact | Purpose |
|---|---|
| `dashboard/Superstore_Sales.pbix` | Power BI dashboard and data model |
| `notebooks/Superstore_Shipping_Regional_Analysis.ipynb` | Reproducible Python analysis |
| `docs/shipping_region_analysis.html` | Lightweight interactive web dashboard |
| `docs/Superstore_Sales_Report.docx` | Full project report and recommendations |
| `data/Sample - Superstore.csv` | Source dataset used by the analysis |

## Power BI dashboard

The Power BI deliverable contains four narrative pages: **Executive Summary, Product Analysis, Customer Analysis, and Regional Performance**. The report describes a model with a dedicated DateTable, a `_Measures` table, calculated columns for discount tier/profit flag/days to ship, and DAX measures for sales, profit, margin, customers, orders, AOV, and shipping performance.

The Regional Performance page is the key operational/business-analysis component: it combines regional KPIs, sales by ship mode, sales distribution, average ship days, late shipments, and profit-margin comparisons.

## Methodology

1. Load and type the Superstore transactional data.
2. Create `Days to Ship` from `Ship Date - Order Date`.
3. Aggregate sales, profit, orders, and margins by region.
4. Compare shipping-mode sales and average delivery time across regions.
5. Define late Standard Class shipments as **more than five calendar days**.
6. Interpret the evidence together rather than treating correlation or operational proximity as proof of causality.

## Tools

- Python — pandas, NumPy, matplotlib
- Power BI Desktop — Power Query, DAX, interactive dashboarding
- HTML / JavaScript — lightweight presentation dashboard

## Repository structure

```text
superstore-shipping-region-analysis/
├── README.md
├── data/
│   └── Sample - Superstore.csv
├── notebooks/
│   └── Superstore_Shipping_Regional_Analysis.ipynb
├── docs/
│   ├── Superstore_Sales_Report.docx
│   └── shipping_region_analysis.html
└── dashboard/
    └── Superstore_Sales.pbix
```

## Important note

This is a **portfolio presentation of a group academic project**. The report and dashboard should be read as the team deliverable; the repository is organized to make the analytical workflow and final artifacts easy for a recruiter or reviewer to inspect.

## Dataset

The supplied report identifies the source as the **Sample Superstore** dataset published on Kaggle by Tableau Software.
