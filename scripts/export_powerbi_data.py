"""Build Power BI-ready CSVs, SQLite tables, and automatically generated insights."""

import sqlite3
from pathlib import Path

import pandas as pd


def export_outputs(root: Path) -> None:
    processed = root / "data" / "processed"
    output = root / "outputs"
    output.mkdir(exist_ok=True)
    orders = pd.read_csv(processed / "orders_clean.csv", parse_dates=["order_date", "customer_signup_date"])
    customers = pd.read_csv(processed / "customers_summary.csv", parse_dates=["customer_signup_date", "last_order_date"])
    completed = orders[orders["is_completed"]].copy()
    completed["order_month"] = completed["order_date"].dt.to_period("M").astype(str)
    first_order = completed.groupby("customer_id")["order_date"].min().rename("first_order_date")
    completed = completed.join(first_order, on="customer_id")
    completed["customer_type"] = completed["order_date"].eq(completed["first_order_date"]).map({True: "New", False: "Returning"})

    monthly = completed.groupby("order_month").agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), customers=("customer_id", "nunique"), gross_profit=("gross_profit", "sum"), discount_amount=("discount_amount", "sum")).reset_index()
    monthly["aov"] = monthly["revenue"] / monthly["orders"]
    monthly["profit_margin"] = monthly["gross_profit"] / monthly["revenue"]
    monthly["revenue_growth"] = monthly["revenue"].pct_change()
    monthly["new_customers"] = completed[completed["customer_type"] == "New"].groupby("order_month")["customer_id"].nunique().reindex(monthly["order_month"]).fillna(0).values
    monthly["returning_customers"] = monthly["customers"] - monthly["new_customers"]
    monthly.to_csv(output / "monthly_kpis.csv", index=False)

    product = completed.groupby(["product_id", "product_name", "category"]).agg(revenue=("revenue", "sum"), units_sold=("quantity", "sum"), orders=("order_id", "nunique"), cost=("cost", "sum"), gross_profit=("gross_profit", "sum"), discount_amount=("discount_amount", "sum")).reset_index()
    product["profit_margin"] = product["gross_profit"] / product["revenue"]
    product.to_csv(output / "product_performance.csv", index=False)
    category = completed.groupby("category").agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), customers=("customer_id", "nunique"), cost=("cost", "sum"), gross_profit=("gross_profit", "sum"), discount_amount=("discount_amount", "sum")).reset_index()
    category["profit_margin"] = category["gross_profit"] / category["revenue"]
    category.to_csv(output / "category_performance.csv", index=False)

    customer_export = customers.copy()
    customer_export["estimated_clv"] = customer_export["average_order_value"] * customer_export["frequency"] * 1.35
    customer_export.to_csv(output / "customers_summary.csv", index=False)
    customers.groupby("segment").agg(customer_count=("customer_id", "nunique"), revenue=("monetary", "sum"), average_order_value=("average_order_value", "mean"), churn_rate=("is_churned", "mean")).reset_index().to_csv(output / "customer_segments.csv", index=False)

    acquisition = completed.groupby("customer_acquisition_channel").agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), customers=("customer_id", "nunique"), gross_profit=("gross_profit", "sum")).reset_index()
    acquisition["aov"] = acquisition["revenue"] / acquisition["orders"]
    acquisition["profit_margin"] = acquisition["gross_profit"] / acquisition["revenue"]
    acquisition["revenue_per_customer"] = acquisition["revenue"] / acquisition["customers"]
    acquisition.to_csv(output / "acquisition_channel_performance.csv", index=False)

    cohort = pd.read_csv(processed / "cohort_retention.csv")
    cohort.to_csv(output / "cohort_retention.csv", index=False)
    funnel = pd.read_csv(processed / "funnel_clean.csv")
    funnel_totals = funnel[["website_sessions", "product_views", "add_to_cart", "checkout_started", "purchases"]].sum()
    funnel_metrics = pd.DataFrame([{"sessions": funnel_totals.website_sessions, "product_views": funnel_totals.product_views, "add_to_cart": funnel_totals.add_to_cart, "checkout_started": funnel_totals.checkout_started, "purchases": funnel_totals.purchases, "product_view_rate": funnel_totals.product_views / funnel_totals.website_sessions, "add_to_cart_rate": funnel_totals.add_to_cart / funnel_totals.product_views, "checkout_rate": funnel_totals.checkout_started / funnel_totals.add_to_cart, "purchase_conversion_rate": funnel_totals.purchases / funnel_totals.website_sessions, "checkout_dropoff_rate": 1 - funnel_totals.purchases / funnel_totals.checkout_started}])
    funnel_metrics.to_csv(output / "funnel_metrics.csv", index=False)

    insights = [
        f"{category.loc[category.revenue.idxmax(), 'category']} is the top revenue category at ${category.revenue.max():,.0f}.",
        f"{category.loc[category.profit_margin.idxmin(), 'category']} has the weakest category margin at {category.profit_margin.min():.1%}; review pricing and discount depth.",
        f"{product.loc[product.revenue.idxmax(), 'product_name']} is the leading product by revenue at ${product.revenue.max():,.0f}.",
        f"{product.loc[product.profit_margin.idxmin(), 'product_name']} has the lowest product margin at {product.profit_margin.min():.1%}.",
        f"Returning customers contribute {len(completed[completed.customer_type == 'Returning']) / len(completed):.1%} of completed order lines.",
        f"The overall churn rate is {customers.is_churned.mean():.1%} using a 90-day inactivity definition.",
        f"{customers.groupby('segment').monetary.sum().idxmax()} contributes the most customer revenue.",
        f"{acquisition.loc[acquisition.revenue_per_customer.idxmax(), 'customer_acquisition_channel']} has the highest revenue per acquired customer.",
        f"The purchase conversion rate is {funnel_metrics.purchase_conversion_rate.iloc[0]:.1%}; checkout drop-off is {funnel_metrics.checkout_dropoff_rate.iloc[0]:.1%}.",
        f"Discounts reduce gross sales by ${completed.discount_amount.sum():,.0f}; prioritize tests that protect margin.",
        f"The most recent cohort has {cohort[cohort.period_number == 3].retention_rate.mean():.1%} average month-3 retention where observable.",
    ]
    (output / "business_insights.md").write_text("# Automatically Generated Business Insights\n\n" + "\n".join(f"- {insight}" for insight in insights) + "\n", encoding="utf-8")

    database = root / "data" / "ecommerce.sqlite"
    with sqlite3.connect(database) as connection:
        orders.to_sql("orders", connection, if_exists="replace", index=False)
        customers.to_sql("customers", connection, if_exists="replace", index=False)
        funnel.to_sql("funnel", connection, if_exists="replace", index=False)
        product.to_sql("product_performance", connection, if_exists="replace", index=False)
        category.to_sql("category_performance", connection, if_exists="replace", index=False)


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])