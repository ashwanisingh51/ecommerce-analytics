-- Run against data/ecommerce.sqlite after scripts/export_powerbi_data.py.

-- Executive KPIs
SELECT ROUND(SUM(revenue), 2) AS total_revenue,
       COUNT(DISTINCT order_id) AS orders,
       COUNT(DISTINCT customer_id) AS customers,
       ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS aov,
       ROUND(SUM(gross_profit), 2) AS gross_profit,
       ROUND(SUM(gross_profit) / SUM(revenue), 4) AS profit_margin
FROM orders WHERE is_completed = 1;

-- Monthly revenue and growth
WITH monthly AS (
    SELECT order_month, SUM(revenue) revenue
    FROM orders WHERE is_completed = 1 GROUP BY order_month
)
SELECT order_month, ROUND(revenue, 2) revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY order_month)) /
             NULLIF(LAG(revenue) OVER (ORDER BY order_month), 0), 4) revenue_growth
FROM monthly ORDER BY order_month;

-- Product and category performance
SELECT product_name, category, ROUND(SUM(revenue), 2) revenue,
       ROUND(SUM(gross_profit), 2) gross_profit,
       ROUND(SUM(gross_profit) / NULLIF(SUM(revenue), 0), 4) profit_margin
FROM orders WHERE is_completed = 1 GROUP BY product_id, product_name, category
ORDER BY revenue DESC;

SELECT category, ROUND(SUM(revenue), 2) revenue, ROUND(SUM(gross_profit), 2) gross_profit,
       ROUND(SUM(gross_profit) / NULLIF(SUM(revenue), 0), 4) profit_margin
FROM orders WHERE is_completed = 1 GROUP BY category ORDER BY revenue DESC;

-- New versus returning customers
WITH first_order AS (SELECT customer_id, MIN(order_date) first_order_date FROM orders WHERE is_completed = 1 GROUP BY customer_id)
SELECT CASE WHEN o.order_date = f.first_order_date THEN 'New' ELSE 'Returning' END customer_type,
       COUNT(DISTINCT o.order_id) orders, ROUND(SUM(o.revenue), 2) revenue
FROM orders o JOIN first_order f USING (customer_id) WHERE o.is_completed = 1
GROUP BY customer_type;

-- Customer purchase frequency and CLV proxy
SELECT customer_id, COUNT(DISTINCT order_id) purchase_frequency,
       ROUND(SUM(revenue), 2) historical_value,
       ROUND(AVG(revenue) * COUNT(DISTINCT order_id) * 1.35, 2) estimated_clv
FROM orders WHERE is_completed = 1 GROUP BY customer_id ORDER BY estimated_clv DESC;

-- Revenue by geography and channel
SELECT state_region, city, ROUND(SUM(revenue), 2) revenue
FROM orders WHERE is_completed = 1 GROUP BY state_region, city ORDER BY revenue DESC;
SELECT customer_acquisition_channel, ROUND(SUM(revenue), 2) revenue,
       COUNT(DISTINCT customer_id) customers,
       ROUND(SUM(revenue) / COUNT(DISTINCT customer_id), 2) revenue_per_customer
FROM orders WHERE is_completed = 1 GROUP BY customer_acquisition_channel ORDER BY revenue_per_customer DESC;

-- Pareto customers: cumulative revenue contribution
WITH customer_revenue AS (
    SELECT customer_id, SUM(revenue) revenue FROM orders WHERE is_completed = 1 GROUP BY customer_id
), ranked AS (
    SELECT customer_id, revenue, SUM(revenue) OVER (ORDER BY revenue DESC ROWS UNBOUNDED PRECEDING) cumulative_revenue,
           SUM(revenue) OVER () total_revenue FROM customer_revenue
)
SELECT *, ROUND(cumulative_revenue / total_revenue, 4) cumulative_share,
       CASE WHEN cumulative_revenue / total_revenue <= 0.80 THEN 'Top 80% contributor' ELSE 'Long tail' END customer_group
FROM ranked ORDER BY revenue DESC;

-- Churn proxy: inactive for more than 90 days against the latest order date
WITH last_purchase AS (
    SELECT customer_id, MAX(order_date) last_order_date FROM orders WHERE is_completed = 1 GROUP BY customer_id
), max_date AS (SELECT MAX(order_date) analysis_date FROM orders)
SELECT COUNT(*) churned_customers,
       ROUND(100.0 * SUM(CASE WHEN julianday(analysis_date) - julianday(last_order_date) > 90 THEN 1 ELSE 0 END) / COUNT(*), 2) churn_rate
FROM last_purchase CROSS JOIN max_date;