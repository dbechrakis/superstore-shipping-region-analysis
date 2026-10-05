# Power BI report map

What the archived [`Superstore_Sales.pbix`](../dashboard/Superstore_Sales.pbix) contains, read directly from its `Report/Layout` definition so the report can be reviewed without Power BI Desktop. Text boxes and decorative shapes are omitted. Each page is 1280 × 720.

The report is an archived group deliverable and was not recalculated; the [Python and SQL outputs](../outputs/) are the current reference for figures.

## Intro

| Visual | Title | Fields and measures |
|---|---|---|
| Slicer | — | Category |

## Executive Summary

| Visual | Title | Fields and measures |
|---|---|---|
| KPI card | — | Total Sales |
| KPI card | — | Total Profit |
| KPI card | — | Profit Margin |
| KPI card | — | Total Orders |
| Column chart | Revenue & Profit by Year | Date: Year, Total Sales, Total Profit |
| Donut chart | — | Category, Total Sales |
| Bar chart | Revenue & Profit by Region | Region, Total Sales, Total Profit |
| Bar chart | Top 3 Sub-Categories by Profit | Sub-Category, Total Sales, Total Profit |

## Product Analysis

| Visual | Title | Fields and measures |
|---|---|---|
| Bar chart | Revenue & Profit by Sub-Category | Total Sales, Total Profit, Sub-Category |
| Column chart | Profit Margin by Category | Category, Profit Margin |
| Line chart | Monthly Sales Trend by Year | Date: Month Name, Total Sales, Year |
| Scatter chart | Discount vs Profit by Sub-Category | Total Profit, Sub-Category, Category, Avg Discount |
| Slicer | — | Category |
| Slicer | — | Year |
| Slicer | — | Region |

## Regional Performance

| Visual | Title | Fields and measures |
|---|---|---|
| KPI card | West | Total Sales, Total Profit, Total Orders, Profit Margin |
| KPI card | East | Total Sales, Total Profit, Total Orders, Profit Margin |
| KPI card | Central | Total Sales, Total Profit, Total Orders, Profit Margin |
| KPI card | South | Total Sales, Total Profit, Total Orders, Profit Margin |
| Column chart | Sales by Ship Mode per Region | Ship Mode, Total Orders, Total Profit, Profit Margin, Region, Total Sales |
| Donut chart | Sales Distribution by Region | Region, Total Sales, Total Orders, Total Profit, Profit Margin |
| Matrix | Avg Ship Days — Region × Mode | Ship Mode, Region, Avg Days to Ship |
| Bar chart | Late Shipments — Standard Class >5 Days | Region, Late Shipments |
| Matrix | Avg Ship Days — Region × Mode | Region, Profit Margin, Ship Mode |

The second matrix on this page reuses the title *Avg Ship Days — Region × Mode* but displays **Profit Margin** by region and ship mode; its title should be corrected in Power BI Desktop.

## Customer Analysis

| Visual | Title | Fields and measures |
|---|---|---|
| KPI card | — | Avg Sale per Customer, Total Customers |
| KPI card | — | Avg Order Value, Total Orders |
| Line + column combo | — | Date: Month Name, Total Customers, Total Profit |
| Column chart | — | Profit Margin, Region, Segment |
| Table | Top 10 customers by Sales | Date: Customer Rank, Customer Name, Total Sales, Total Profit, Total Orders, Profit Margin |
| Donut chart | — | Total Sales, Segment |
| Bar chart | — | Total Customers, Segment |
| Slicer | — | Segment |
| Slicer | — | Date: Year |
| Slicer | — | Region |

## Measures used

Defined in the `_Measures` table and referenced by the visuals above: `Avg Days to Ship`, `Avg Discount`, `Avg Order Value`, `Avg Sale per Customer`, `Late Shipments`, `Profit Margin`, `Total Customers`, `Total Orders`, `Total Profit`, `Total Sales`.

The model also uses a dedicated `DateTable` for year and month slicing.
