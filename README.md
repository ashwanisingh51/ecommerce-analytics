# E-commerce Revenue & Customer Analytics

An end-to-end analyst portfolio project that turns reproducible order, customer, and web-funnel data into revenue, profitability, retention, churn, segmentation, and acquisition insights. The project is designed for Data Analyst, Business Analyst, Product Analyst, and Growth Analyst roles.

## Business Problem

The business needs to understand what drives profitable revenue, which customers are worth retaining, where customers fall out of the funnel, and which products, geographies, and acquisition channels deserve investment. This project answers those questions with Python, SQL, and Power BI-ready exports.

## Dataset

The included generator creates 18,000 order lines for 2,500 customers across January 2024 to June 2025. Fields include order, product, price, cost, discount, payment, geography, signup, acquisition channel, and order status. It also creates weekly synthetic funnel observations with sessions, product views, add-to-cart, checkout, and purchases. A fixed random seed makes the data fully reproducible without external downloads.

## Tech Stack

Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter, SQLite, SQL, and Power BI-ready CSV files.

## KPIs and Analysis

- Revenue, orders, unique customers, AOV, gross profit, and profit margin
- Monthly growth, new versus returning customers, product/category performance, and geography
- RFM segmentation: Champions, Loyal Customers, Potential Loyalists, New Customers, At Risk, and Lost Customers
- Customer lifetime value proxy, purchase frequency, Pareto contribution, 90-day churn, and churn drivers
- Monthly cohort size, retention rates, and retention heatmap
- Funnel conversion and drop-off from sessions to purchase
- Discount impact, low-margin/high-revenue products, and cancellation/return leakage

## Dashboard Pages

The [Power BI dashboard plan](powerbi/dashboard_plan.md) specifies five pages: Executive Overview; Revenue and Product Performance; Customer Analytics; Retention and Churn; and Growth and Acquisition. The `outputs/` folder contains clean files for direct import.

## Key Insights

Run the pipeline to generate `outputs/business_insights.md` with eleven data-driven observations based on the current sample. The output includes top and low-margin categories/products, returning-customer contribution, churn, channel value, funnel conversion, discount leakage, and cohort retention.

## Business Recommendations

1. Build triggered win-back campaigns for high-value At Risk customers before the 90-day churn threshold.
2. Shift acquisition budget toward channels with high revenue per customer and healthy profit margin, not volume alone.
3. Audit low-margin/high-revenue products for supplier cost, pricing, and promotion changes.
4. Use bundles and personalized cross-sells to move New Customers toward repeat purchase behavior.
5. Test improvements at the largest funnel drop-off stage and monitor conversion by channel weekly.
6. Replace broad discounting with segment-specific offers and measure incremental gross profit.

## Repository Structure

```text
ecommerce-analytics/
├── data/raw/                 # Generated source CSVs
├── data/processed/           # Clean orders, customers, funnel, cohorts
├── notebooks/                # Four analyst workflow notebooks
├── sql/                      # SQLite schema and analysis queries
├── scripts/                  # Dataset, cleaning, and export modules
├── powerbi/                  # Dashboard build plan
├── outputs/                  # Power BI CSVs, insights, and charts
├── requirements.txt
└── README.md
```

## How to Run

From the project root:

```bash
python -m pip install -r requirements.txt
python scripts/generate_dataset.py
python scripts/data_cleaning.py
python scripts/export_powerbi_data.py
```

The commands create raw data, clean/enriched data, `data/ecommerce.sqlite`, nine Power BI-ready CSV outputs, and generated business insights. Open the notebooks from the project root or run `jupyter notebook notebooks` for exploratory visuals.

## Resume Bullets

- Built a reproducible e-commerce analytics pipeline for 18K order lines and 2.5K customers using Python, Pandas, NumPy, SQLite, and Power BI-ready exports.
- Developed SQL and Python KPI analysis covering revenue growth, AOV, gross margin, product economics, acquisition efficiency, funnel conversion, and 90-day churn.
- Applied RFM segmentation and monthly cohort analysis to quantify customer value, identify high-value at-risk audiences, and measure retention through month 3.
- Identified discount leakage, low-margin/high-revenue products, channel efficiency gaps, and funnel drop-offs, translating findings into six prioritized growth and profitability recommendations.