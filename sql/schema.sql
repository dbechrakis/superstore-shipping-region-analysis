CREATE TABLE order_lines (
    row_id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    region TEXT NOT NULL,
    segment TEXT NOT NULL,
    sales_micros INTEGER NOT NULL CHECK (sales_micros > 0),
    profit_micros INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    discount REAL NOT NULL CHECK (discount BETWEEN 0 AND 1)
);
CREATE INDEX lines_order ON order_lines(order_id);
CREATE INDEX lines_customer_date ON order_lines(customer_id, order_date);

-- Collapse lines BEFORE applying windows: an order with five products is one purchase.
CREATE VIEW orders AS
SELECT order_id, customer_id, order_date, region, segment,
       SUM(sales_micros) AS sales_micros,
       SUM(profit_micros) AS profit_micros,
       SUM(quantity) AS quantity, COUNT(*) AS lines
FROM order_lines
GROUP BY order_id, customer_id, order_date, region, segment;

CREATE TABLE analysis_scope (as_of TEXT NOT NULL);
CREATE VIEW scoped_orders AS
SELECT o.* FROM orders o CROSS JOIN analysis_scope s
WHERE o.order_date <= s.as_of;

CREATE VIEW customer_order_sequence AS
SELECT o.*,
       ROW_NUMBER() OVER (
           PARTITION BY customer_id ORDER BY order_date, order_id
       ) AS purchase_number,
       MIN(order_date) OVER (PARTITION BY customer_id) AS first_observed_date,
       LAG(order_date) OVER (
           PARTITION BY customer_id ORDER BY order_date, order_id
       ) AS previous_order_date,
       LEAD(order_date) OVER (
           PARTITION BY customer_id ORDER BY order_date, order_id
       ) AS next_order_date,
       SUM(sales_micros) OVER (
           PARTITION BY customer_id ORDER BY order_date, order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_sales_micros
FROM scoped_orders o;
