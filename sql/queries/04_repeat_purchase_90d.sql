-- A customer contributes only when their entire 90-day window is observable.
-- Region/segment are fixed at first observed purchase to avoid future information.
WITH first_orders AS (
    SELECT customer_id, region, segment, order_date, next_order_date,
           date(order_date, '+90 days') <= s.as_of AS eligible,
           CASE WHEN next_order_date IS NOT NULL
                 AND julianday(next_order_date) - julianday(order_date) <= 90
                THEN 1 ELSE 0 END AS repeat_within_90d
    FROM customer_order_sequence CROSS JOIN analysis_scope s
    WHERE purchase_number = 1
), grouped AS (
    SELECT 'all' AS breakdown, 'All customers' AS segment_value,
           COUNT(*) AS observed_customers, SUM(eligible) AS eligible_customers,
           SUM(eligible * repeat_within_90d) AS repeat_customers FROM first_orders
    UNION ALL
    SELECT 'first_order_region', region, COUNT(*), SUM(eligible),
           SUM(eligible * repeat_within_90d) FROM first_orders GROUP BY region
    UNION ALL
    SELECT 'first_order_segment', segment, COUNT(*), SUM(eligible),
           SUM(eligible * repeat_within_90d) FROM first_orders GROUP BY segment
)
SELECT *, observed_customers - eligible_customers AS censored_customers,
       repeat_customers * 1.0 / NULLIF(eligible_customers, 0) AS repeat_rate_90d
FROM grouped ORDER BY breakdown, segment_value;
