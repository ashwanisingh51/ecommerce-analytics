"""Save the key analysis charts as PNG files under outputs/charts."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def make_charts(root: Path) -> None:
    output = root / "outputs"
    charts = output / "charts"
    charts.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    monthly = pd.read_csv(output / "monthly_kpis.csv")
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly["order_month"], monthly["revenue"] / 1000, marker="o", label="Revenue")
    ax.plot(monthly["order_month"], monthly["gross_profit"] / 1000, marker="o", label="Gross profit")
    ax.set_title("Monthly revenue and gross profit")
    ax.set_ylabel("USD (thousands)")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    fig.tight_layout()
    fig.savefig(charts / "monthly_revenue_profit.png", dpi=120)
    plt.close(fig)

    category = pd.read_csv(output / "category_performance.csv").sort_values("revenue")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(category["category"], category["revenue"] / 1000)
    for y, (rev, margin) in enumerate(zip(category["revenue"], category["profit_margin"])):
        ax.text(rev / 1000, y, f"  {margin:.0%} margin", va="center", fontsize=9)
    ax.set_title("Revenue by category")
    ax.set_xlabel("USD (thousands)")
    fig.tight_layout()
    fig.savefig(charts / "category_revenue_margin.png", dpi=120)
    plt.close(fig)

    segments = pd.read_csv(output / "customer_segments.csv").sort_values("revenue")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(segments["segment"], segments["revenue"] / 1000)
    for y, (rev, count) in enumerate(zip(segments["revenue"], segments["customer_count"])):
        ax.text(rev / 1000, y, f"  {count:,} customers", va="center", fontsize=9)
    ax.set_title("Revenue by RFM segment")
    ax.set_xlabel("USD (thousands)")
    fig.tight_layout()
    fig.savefig(charts / "rfm_segment_revenue.png", dpi=120)
    plt.close(fig)

    cohort = pd.read_csv(output / "cohort_retention.csv")
    matrix = cohort[cohort["period_number"] <= 6].pivot(index="cohort_month", columns="period_number", values="retention_rate")
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(matrix, annot=True, fmt=".0%", cmap="Blues", cbar=False, ax=ax)
    ax.set_title("Monthly cohort retention (months 0 to 6)")
    ax.set_xlabel("Months since first purchase")
    ax.set_ylabel("First purchase month")
    fig.tight_layout()
    fig.savefig(charts / "cohort_retention_heatmap.png", dpi=120)
    plt.close(fig)

    funnel = pd.read_csv(output / "funnel_metrics.csv").iloc[0]
    stages = ["sessions", "product_views", "add_to_cart", "checkout_started", "purchases"]
    values = [funnel[s] for s in stages]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar([s.replace("_", " ").title() for s in stages], values)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value / values[0]:.1%}", ha="center", va="bottom", fontsize=9)
    ax.set_title("Website funnel (share of sessions)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(charts / "funnel_conversion.png", dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    make_charts(Path(__file__).resolve().parents[1])
