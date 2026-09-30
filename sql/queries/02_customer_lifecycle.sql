SELECT customer_id, MIN(order_date) AS first_observed_date,
       MAX(order_date) AS last_observed_date, COUNT(*) AS orders,
       SUM(sales_micros) / 1000000.0 AS sales,
       SUM(profit_micros) / 1000000.0 AS profit,
       SUM(profit_micros) * 1.0 / SUM(sales_micros) AS profit_margin,
       MAX(CASE WHEN purchase_number = 1 THEN next_order_date END) AS second_order_date,
       MAX(CASE WHEN purchase_number = 1 THEN region END) AS first_order_region,
       MAX(CASE WHEN purchase_number = 1 THEN segment END) AS first_order_segment,
       CAST(julianday((SELECT as_of FROM analysis_scope)) - julianday(MAX(order_date))
            AS INTEGER) AS days_since_last_order
FROM customer_order_sequence
GROUP BY customer_id ORDER BY customer_id;
