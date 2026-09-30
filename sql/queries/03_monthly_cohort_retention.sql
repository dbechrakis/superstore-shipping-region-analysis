-- Full calendar-month activity after FIRST OBSERVED purchase, not acquisition.
-- Keep unobservable cells NULL and observable cells with no activity at zero.
WITH RECURSIVE ages(age_months) AS (
    SELECT 0 UNION ALL SELECT age_months + 1 FROM ages WHERE age_months < 12
), membership AS (
    SELECT customer_id, date(MIN(order_date), 'start of month') AS cohort_month
    FROM scoped_orders GROUP BY customer_id
), cohorts AS (
    SELECT cohort_month, COUNT(*) AS cohort_customers
    FROM membership GROUP BY cohort_month
), activity AS (
    SELECT m.cohort_month, date(o.order_date, 'start of month') AS activity_month,
           COUNT(DISTINCT o.customer_id) AS active_customers
    FROM scoped_orders o JOIN membership m USING (customer_id)
    GROUP BY m.cohort_month, activity_month
), grid AS (
    SELECT c.*, a.age_months,
           date(c.cohort_month, '+' || a.age_months || ' months') AS activity_month
    FROM cohorts c CROSS JOIN ages a
)
SELECT g.cohort_month, g.age_months, g.activity_month, g.cohort_customers,
       CASE WHEN g.activity_month >= (SELECT MIN(order_date) FROM scoped_orders)
                 AND date(g.activity_month, '+1 month', '-1 day') <= s.as_of
            THEN 1 ELSE 0 END AS observable,
       CASE WHEN g.activity_month >= (SELECT MIN(order_date) FROM scoped_orders)
                 AND date(g.activity_month, '+1 month', '-1 day') <= s.as_of
            THEN COALESCE(a.active_customers, 0) END AS active_customers,
       CASE WHEN g.activity_month >= (SELECT MIN(order_date) FROM scoped_orders)
                 AND date(g.activity_month, '+1 month', '-1 day') <= s.as_of
            THEN COALESCE(a.active_customers, 0) * 1.0 / g.cohort_customers END AS retention_rate
FROM grid g CROSS JOIN analysis_scope s
LEFT JOIN activity a ON g.cohort_month = a.cohort_month
                   AND g.activity_month = a.activity_month
ORDER BY g.cohort_month, g.age_months;
