SELECT COUNT(*) AS orders, COUNT(DISTINCT customer_id) AS customers,
       SUM(lines) AS order_lines, SUM(sales_micros) AS sales_micros,
       SUM(profit_micros) AS profit_micros,
       MIN(order_date) AS observation_start, MAX(order_date) AS last_order_date,
       (SELECT as_of FROM analysis_scope) AS as_of
FROM scoped_orders;
