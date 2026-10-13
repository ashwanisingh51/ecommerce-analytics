-- SQLite-compatible analytical schema. The Python export script creates these tables.
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT, customer_id TEXT, order_date TEXT, product_id TEXT,
    product_name TEXT, category TEXT, quantity INTEGER, unit_price REAL,
    discount REAL, cost_price REAL, payment_method TEXT, city TEXT,
    state_region TEXT, customer_acquisition_channel TEXT,
    customer_signup_date TEXT, order_status TEXT, gross_revenue REAL,
    revenue REAL, cost REAL, gross_profit REAL, profit_margin REAL,
    discount_amount REAL, order_month TEXT, order_year INTEGER,
    customer_tenure_days INTEGER, is_completed INTEGER
);

CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
