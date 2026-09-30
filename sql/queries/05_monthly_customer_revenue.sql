-- Date spine ensures LAG refers to the preceding calendar month, even with no orders.
WITH RECURSIVE months(month) AS (
    SELECT date(MIN(order_date), 'start of month') FROM scoped_orders
    UNION ALL
    SELECT date(month, '+1 month') FROM months
    WHERE date(month, '+1 month') <= date((SELECT as_of FROM analysis_scope), 'start of month')
), activity AS (
    SELECT date(order_date, 'start of month') AS month,
           COUNT(*) AS orders, COUNT(DISTINCT customer_id) AS active_customers,
           SUM(sales_micros) / 1000000.0 AS sales,
           SUM(profit_micros) / 1000000.0 AS profit,
           SUM(CASE WHEN purchase_number = 1 THEN sales_micros ELSE 0 END) / 1000000.0
               AS first_order_sales
    FROM customer_order_sequence GROUP BY month
), complete_months AS (
    SELECT m.month, COALESCE(a.orders, 0) AS orders,
           COALESCE(a.active_customers, 0) AS active_customers,
           COALESCE(a.sales, 0.0) AS sales, COALESCE(a.profit, 0.0) AS profit,
           COALESCE(a.first_order_sales, 0.0) AS first_order_sales
    FROM months m LEFT JOIN activity a USING (month)
    WHERE m.month >= (SELECT MIN(order_date) FROM scoped_orders)
      AND date(m.month, '+1 month', '-1 day') <= (SELECT as_of FROM analysis_scope)
), lagged AS (
    SELECT *, sales - first_order_sales AS repeat_order_sales,
           LAG(sales) OVER (ORDER BY month) AS previous_month_sales,
           SUM(sales) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
               AS rolling_3m_sales,
           COUNT(*) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
               AS rolling_months
    FROM complete_months
)
SELECT *, (sales - previous_month_sales) / NULLIF(previous_month_sales, 0)
              AS sales_change_vs_previous_month
FROM lagged ORDER BY month;
