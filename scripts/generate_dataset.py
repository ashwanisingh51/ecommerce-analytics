"""Generate a reproducible synthetic e-commerce dataset for portfolio analysis."""

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 42
END_DATE = pd.Timestamp("2025-06-30")
START_DATE = pd.Timestamp("2024-01-01")


def generate_dataset(output_dir: Path, customer_count: int = 2500, order_count: int = 18000) -> None:
    rng = np.random.default_rng(SEED)
    output_dir.mkdir(parents=True, exist_ok=True)

    catalog = pd.DataFrame(
        [
            ("P001", "Aurora Wireless Headphones", "Electronics", 89, 42),
            ("P002", "Pulse Fitness Watch", "Electronics", 129, 65),
            ("P003", "Nimbus Bluetooth Speaker", "Electronics", 59, 25),
            ("P004", "Lumen Desk Lamp", "Home & Living", 44, 18),
            ("P005", "Terra Ceramic Set", "Home & Living", 68, 31),
            ("P006", "Breeze Air Purifier", "Home & Living", 179, 102),
            ("P007", "Move Everyday Sneakers", "Fashion", 74, 36),
            ("P008", "Arc Trail Jacket", "Fashion", 118, 57),
            ("P009", "Canvas Utility Backpack", "Fashion", 62, 28),
            ("P010", "Focus Notebook Bundle", "Stationery", 24, 8),
            ("P011", "Studio Gel Pen Set", "Stationery", 16, 5),
            ("P012", "Craft Desk Organizer", "Stationery", 32, 13),
            ("P013", "Harvest Coffee Beans", "Grocery", 22, 9),
            ("P014", "Garden Snack Box", "Grocery", 38, 19),
            ("P015", "Daily Wellness Pack", "Health & Wellness", 49, 22),
        ],
        columns=["product_id", "product_name", "category", "base_price", "base_cost"],
    )
    states = {
        "CA": ["Los Angeles", "San Diego", "San Jose"],
        "TX": ["Austin", "Dallas", "Houston"],
        "NY": ["New York", "Buffalo", "Rochester"],
        "FL": ["Miami", "Orlando", "Tampa"],
        "WA": ["Seattle", "Tacoma", "Spokane"],
        "IL": ["Chicago", "Naperville", "Peoria"],
        "CO": ["Denver", "Boulder", "Aurora"],
        "GA": ["Atlanta", "Savannah", "Augusta"],
    }
    state_values = list(states)
    state_weights = np.array([0.20, 0.16, 0.14, 0.12, 0.10, 0.11, 0.09, 0.08])
    channels = ["Paid Search", "Organic Search", "Email", "Social", "Affiliate", "Direct"]
    channel_weights = [0.24, 0.22, 0.16, 0.15, 0.10, 0.13]

    customer_ids = [f"C{i:05d}" for i in range(1, customer_count + 1)]
    signup_dates = pd.to_datetime(
        rng.integers(START_DATE.value // 86_400_000_000_000, (END_DATE - pd.Timedelta(days=30)).value // 86_400_000_000_000, customer_count),
        unit="D",
    )
    customer_channels = rng.choice(channels, customer_count, p=channel_weights)
    customer_states = rng.choice(state_values, customer_count, p=state_weights)
    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "customer_signup_date": signup_dates,
            "customer_acquisition_channel": customer_channels,
            "state_region": customer_states,
        }
    )

    # A gamma-distributed propensity creates a realistic long tail of repeat buyers.
    propensity = rng.gamma(shape=1.5, scale=1.0, size=customer_count)
    propensity = propensity / propensity.sum()
    order_customer_idx = rng.choice(customer_count, order_count, p=propensity)
    order_dates = []
    for customer_idx in order_customer_idx:
        lower = max(START_DATE, signup_dates[customer_idx])
        order_dates.append(lower + pd.Timedelta(days=int(rng.integers(0, max(1, (END_DATE - lower).days + 1)))))

    product_idx = rng.choice(len(catalog), order_count, p=[0.08, 0.07, 0.06, 0.07, 0.06, 0.04, 0.10, 0.07, 0.06, 0.08, 0.07, 0.05, 0.08, 0.06, 0.10])
    quantities = rng.choice([1, 2, 3, 4], order_count, p=[0.66, 0.22, 0.09, 0.03])
    discounts = rng.choice([0, 0.05, 0.10, 0.15, 0.25], order_count, p=[0.38, 0.25, 0.22, 0.11, 0.04])
    statuses = rng.choice(["Delivered", "Shipped", "Cancelled", "Returned"], order_count, p=[0.82, 0.08, 0.06, 0.04])
    payment_methods = rng.choice(["Card", "UPI", "Wallet", "COD", "Bank Transfer"], order_count, p=[0.48, 0.20, 0.12, 0.14, 0.06])
    rows = []
    for i in range(order_count):
        product = catalog.iloc[product_idx[i]]
        customer_idx = order_customer_idx[i]
        state = customers.iloc[customer_idx]["state_region"]
        rows.append(
            {
                "order_id": f"O{i + 1:06d}",
                "customer_id": customer_ids[customer_idx],
                "order_date": order_dates[i],
                "product_id": product.product_id,
                "product_name": product.product_name,
                "category": product.category,
                "quantity": int(quantities[i]),
                "unit_price": round(float(product.base_price) * rng.uniform(0.92, 1.10), 2),
                "discount": float(discounts[i]),
                "cost_price": round(float(product.base_cost) * rng.uniform(0.94, 1.06), 2),
                "payment_method": payment_methods[i],
                "city": rng.choice(states[state]),
                "state_region": state,
                "customer_acquisition_channel": customers.iloc[customer_idx]["customer_acquisition_channel"],
                "customer_signup_date": signup_dates[customer_idx],
                "order_status": statuses[i],
            }
        )
    orders = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)
    orders.to_csv(output_dir / "orders_raw.csv", index=False)

    # Funnel rows are weekly channel observations and are intentionally independent of order rows.
    weeks = pd.date_range(START_DATE, END_DATE, freq="W-MON")
    funnel_rows = []
    for week in weeks:
        for channel, weight in zip(channels, channel_weights):
            sessions = int(rng.normal(4200 * weight, 420 * max(weight, 0.5)))
            sessions = max(250, sessions)
            product_views = int(sessions * rng.uniform(0.62, 0.78))
            add_to_cart = int(product_views * rng.uniform(0.16, 0.28))
            checkout_started = int(add_to_cart * rng.uniform(0.52, 0.74))
            purchases = int(checkout_started * rng.uniform(0.58, 0.82))
            funnel_rows.append({"week": week, "channel": channel, "website_sessions": sessions, "product_views": product_views, "add_to_cart": add_to_cart, "checkout_started": checkout_started, "purchases": purchases})
    pd.DataFrame(funnel_rows).to_csv(output_dir / "funnel_raw.csv", index=False)


if __name__ == "__main__":
    generate_dataset(Path(__file__).resolve().parents[1] / "data" / "raw")