"""Clean raw data and create reusable customer and cohort analysis tables."""

from pathlib import Path

import numpy as np
import pandas as pd


def clean_orders(raw_dir: Path, processed_dir: Path) -> pd.DataFrame:
    orders = pd.read_csv(raw_dir / "orders_raw.csv", parse_dates=["order_date", "customer_signup_date"])
    orders = orders.drop_duplicates(subset=["order_id", "product_id"])
    orders["category"] = orders["category"].str.strip().replace({"Home and Living": "Home & Living"})
    orders["quantity"] = pd.to_numeric(orders["quantity"], errors="coerce")
    for column in ["unit_price", "discount", "cost_price"]:
        orders[column] = pd.to_numeric(orders[column], errors="coerce")
    orders = orders.dropna(subset=["order_id", "customer_id", "order_date", "product_id", "quantity", "unit_price", "cost_price"])
    orders = orders[(orders["quantity"] > 0) & (orders["unit_price"] > 0) & (orders["cost_price"] >= 0)]
    orders["discount"] = orders["discount"].clip(lower=0, upper=0.90).fillna(0)
    orders["gross_revenue"] = orders["quantity"] * orders["unit_price"]
    orders["revenue"] = orders["gross_revenue"] * (1 - orders["discount"])
    orders["cost"] = orders["quantity"] * orders["cost_price"]
    orders["gross_profit"] = orders["revenue"] - orders["cost"]
    orders["profit_margin"] = np.where(orders["revenue"] > 0, orders["gross_profit"] / orders["revenue"], 0)
    orders["discount_amount"] = orders["gross_revenue"] - orders["revenue"]
    orders["order_month"] = orders["order_date"].dt.to_period("M").astype(str)
    orders["order_year"] = orders["order_date"].dt.year
    orders["customer_tenure_days"] = (orders["order_date"] - orders["customer_signup_date"]).dt.days.clip(lower=0)
    orders["is_completed"] = orders["order_status"].isin(["Delivered", "Shipped"])
    orders.to_csv(processed_dir / "orders_clean.csv", index=False)
    return orders


def build_customer_tables(orders: pd.DataFrame, processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    completed = orders[orders["is_completed"]].copy()
    analysis_date = orders["order_date"].max() + pd.Timedelta(days=1)
    customer_base = orders.sort_values("customer_signup_date").drop_duplicates("customer_id")[["customer_id", "customer_signup_date", "customer_acquisition_channel", "state_region"]]
    rfm = completed.groupby("customer_id").agg(
        last_order_date=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
        average_order_value=("revenue", "mean"),
    ).reset_index()
    rfm["recency"] = (analysis_date - rfm["last_order_date"]).dt.days
    for metric, ascending in [("recency", False), ("frequency", True), ("monetary", True)]:
        rfm[f"{metric}_score"] = pd.qcut(rfm[metric].rank(method="first"), 5, labels=False) + 1
        if metric == "recency":
            rfm[f"{metric}_score"] = 6 - rfm[f"{metric}_score"]
    rfm["rfm_score"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str) + rfm["monetary_score"].astype(str)

    def segment(row: pd.Series) -> str:
        if row.recency_score >= 4 and row.frequency_score >= 4 and row.monetary_score >= 4:
            return "Champions"
        if row.frequency_score >= 4 and row.recency_score >= 3:
            return "Loyal Customers"
        if row.recency_score >= 4 and row.frequency == 1:
            return "New Customers"
        if row.recency_score >= 4 and row.frequency_score <= 3:
            return "Potential Loyalists"
        if row.recency_score <= 2 and row.frequency_score >= 3:
            return "At Risk"
        return "Lost Customers"

    rfm["segment"] = rfm.apply(segment, axis=1)
    rfm["is_churned"] = rfm["recency"] > 90
    customers = customer_base.merge(rfm, on="customer_id", how="left")
    customers["frequency"] = customers["frequency"].fillna(0).astype(int)
    customers["monetary"] = customers["monetary"].fillna(0)
    customers["average_order_value"] = customers["average_order_value"].fillna(0)
    customers["recency"] = customers["recency"].fillna((analysis_date - customers["customer_signup_date"]).dt.days)
    customers["segment"] = customers["segment"].fillna("New Customers")
    customers["is_churned"] = customers["is_churned"].fillna(True)
    customers.to_csv(processed_dir / "customers_summary.csv", index=False)
    rfm.to_csv(processed_dir / "customer_segments.csv", index=False)
    return customers, completed


def build_cohorts(completed: pd.DataFrame, processed_dir: Path) -> pd.DataFrame:
    first_purchase = completed.groupby("customer_id")["order_date"].min().rename("cohort_date")
    data = completed[["customer_id", "order_date"]].drop_duplicates().join(first_purchase, on="customer_id")
    data["cohort_month"] = data["cohort_date"].dt.to_period("M").astype(str)
    data["activity_month"] = data["order_date"].dt.to_period("M").astype(str)
    data["period_number"] = (data["order_date"].dt.year - data["cohort_date"].dt.year) * 12 + data["order_date"].dt.month - data["cohort_date"].dt.month
    cohort_size = data.groupby("cohort_month")["customer_id"].nunique().rename("cohort_size")
    retention = data.groupby(["cohort_month", "period_number"])["customer_id"].nunique().rename("active_customers").reset_index()
    retention = retention.merge(cohort_size, on="cohort_month")
    retention["retention_rate"] = retention["active_customers"] / retention["cohort_size"]
    retention.to_csv(processed_dir / "cohort_retention.csv", index=False)
    return retention


def run_cleaning(raw_dir: Path, processed_dir: Path) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)
    orders = clean_orders(raw_dir, processed_dir)
    _, completed = build_customer_tables(orders, processed_dir)
    build_cohorts(completed, processed_dir)
    pd.read_csv(raw_dir / "funnel_raw.csv", parse_dates=["week"]).to_csv(processed_dir / "funnel_clean.csv", index=False)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    run_cleaning(root / "data" / "raw", root / "data" / "processed")