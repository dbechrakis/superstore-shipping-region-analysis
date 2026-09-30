-- Descriptive full-window concentration, not a future customer-value model.
WITH customer_sales AS (
    SELECT customer_id, SUM(sales_micros) AS sales_micros,
           SUM(profit_micros) AS profit_micros, COUNT(*) AS orders
    FROM scoped_orders GROUP BY customer_id
)
SELECT customer_id, orders, sales_micros / 1000000.0 AS sales,
       profit_micros / 1000000.0 AS profit,
       DENSE_RANK() OVER (ORDER BY sales_micros DESC) AS sales_rank,
       NTILE(10) OVER (ORDER BY sales_micros DESC, customer_id) AS sales_decile,
       SUM(sales_micros) OVER (
           ORDER BY sales_micros DESC, customer_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) * 1.0 / SUM(sales_micros) OVER () AS cumulative_sales_share
FROM customer_sales ORDER BY sales_micros DESC, customer_id;
