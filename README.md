# Superstore — Regional Profitability & Shipping Analytics

A business intelligence case study using **Python, Power BI, DAX, and an interactive HTML dashboard** to identify regional profitability gaps and understand whether shipping or commercial factors explain performance differences.

## Executive summary

The analysis examines sales, profit margin, shipping performance, and product-level drivers across four US regions.

**Key finding:** Central is the clear profitability outlier, with an approximately **7.92% margin versus 14.94% in West**. Average shipping time is broadly similar across regions, so the evidence points more strongly toward **pricing and discounting** than logistics as the main explanation for the gap.

### Business implications

- Review discounting and pricing in Central, especially within Furniture.
- Prioritize Tables and Bookcases where margin pressure is strongest.
- Keep monitoring Standard Class performance, but avoid treating shipping speed as the primary root cause without stronger evidence.
- Validate commercial interventions with controlled tests before scaling them.

## Business questions

- Which regions generate revenue efficiently, and where is margin leaking?
- Does shipping-mode mix differ materially by region?
- Are delivery times consistent across regions and shipping modes?
- Where are late Standard Class shipments concentrated?
- What operational and commercial explanations are supported by the data?

## Key metrics

| Metric | Result |
|---|---:|
| Sales | **$2.30M** |
| Profit | **$286.40K** |
| Overall margin | **12.47%** |
| Central margin | **7.92%** |
| West margin | **14.94%** |
| Standard Class | Dominant shipping mode |

## Analysis approach

1. Clean and type the transactional data.
2. Build delivery-time and profitability measures.
3. Compare sales, profit, margin, and shipping performance by region and shipping mode.
4. Investigate product and discount patterns behind regional margin differences.
5. Translate the evidence into business recommendations while separating correlation from causation.

## Deliverables

| Artifact | Purpose |
|---|---|
| [`Superstore_Sales.pbix`](dashboard/Superstore_Sales.pbix) | Power BI dashboard and data model |
| [`Superstore_Shipping_Regional_Analysis.ipynb`](notebooks/Superstore_Shipping_Regional_Analysis.ipynb) | Reproducible Python analysis |
| [`shipping_region_analysis.html`](docs/shipping_region_analysis.html) | Interactive HTML dashboard |
| [`Superstore_Sales_Report.docx`](docs/Superstore_Sales_Report.docx) | Detailed analysis and recommendations |

## Dashboard

The Power BI report is structured around four analytical views:

- **Executive Summary** — headline KPIs and regional performance
- **Product Analysis** — product/category profitability and margin pressure
- **Customer Analysis** — customer and order-level patterns
- **Regional Performance** — shipping, margin, sales, and late-shipment analysis

The model uses a dedicated DateTable, a measures table, calculated business flags, and DAX measures for sales, profit, margin, customers, orders, AOV, and shipping performance.

## Tools

**Power BI · DAX · Power Query · Python · pandas · NumPy · matplotlib · HTML / JavaScript**

## Context

Portfolio case study based on a group Data Visualization project at **The American College of Greece**. The team context is retained for transparency; the repository is presented as a professional analytics case study rather than as a coursework archive.

## Dataset

Sample Superstore transactional data, sourced from the dataset used in the original project.

## Author

**Dimitris Bechrakis**  
Business & Data Analyst | M.Sc. Data Science
