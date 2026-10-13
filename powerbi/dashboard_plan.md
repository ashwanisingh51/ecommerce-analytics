# Power BI Dashboard Plan

## Page 1: Executive Overview
Cards for Revenue, Orders, Customers, AOV, Gross Profit, Profit Margin, Purchase Conversion Rate, and Repeat Purchase Rate. Add a monthly revenue and profit trend with slicers for date, category, region, and channel.

## Page 2: Revenue and Product Performance
Use a revenue trend, category bar chart, top-10 product table, revenue-versus-margin scatter plot, and discount amount by product. Flag high-revenue/low-margin products and cancelled or returned orders.

## Page 3: Customer Analytics
Show new versus returning customers, RFM segment distribution, estimated CLV by segment, frequency distribution, and a table of high-value customers with recency, frequency, monetary value, and preferred category.

## Page 4: Retention and Churn
Use the cohort retention matrix, month-1/2/3 retention trend, churn rate by segment/channel/region, and a high-value at-risk customer table. Churn is defined as more than 90 days since a completed purchase.

## Page 5: Growth and Acquisition
Compare channel revenue, revenue per customer, AOV, profit margin, and funnel conversion. Use a waterfall or stacked bar to show drop-off from sessions to purchase and prioritize the largest loss stage.

## Model Notes
- Relate `orders` to `customers` using `customer_id`.
- Use `order_date` as the primary date relationship and `order_month` for trend axes.
- Format rates as percentages and monetary measures as currency.
- Keep cancelled and returned orders available for leakage analysis, but filter `is_completed = 1` for realized revenue KPIs.