# Retail Sales \& Customer Insights -- Data Analytics Capstone

## Project Overview

This project analyzes a retail/e-commerce dataset to understand sales
performance, customer purchasing behavior, product contribution, payment
activity, profitability, delivery performance, and product returns. The
objective is to turn related operational datasets into clear business
metrics and interactive visualizations that can support data-driven
decisions.

The project uses seven related CSV datasets: customers, products,
orders, order items, payments, shipments, and returns. The datasets are
loaded into a Python analysis workflow, related through their keys, and
explored through a Jupyter Notebook and an interactive Streamlit
dashboard.

## Executive Summary

* Analyzed seven related retail/e-commerce datasets covering
customers, products, orders, order items, payments, shipments, and
returns.
* Built an analytical view that connects transaction details with
customer, product, payment, and delivery information.
* Evaluated sales performance using gross revenue, net revenue,
fulfilled orders, and average order value (AOV).
* Reviewed monthly sales trends to identify changes in revenue over
time.
* Compared product and category revenue to identify leading
contributors to sales.
* Examined revenue by region and city to understand geographic sales
distribution.
* Assessed customer purchasing patterns using new and repeat-customer
classifications.
* Reviewed payment methods and payment statuses to understand
transaction activity.
* Analyzed estimated product profit and discount-related sales
patterns.
* Explored shipment, delivery, cancellation, and return-request
information.
* Presented the analysis through notebook outputs, exported charts,
and an interactive Streamlit dashboard.
* Developed recommendations based on the verified results recorded in
the notebook and dashboard.

> Replace or supplement these bullets with final measured results after
> validating the completed notebook and dashboard.

## Project Objectives

1. Combine the seven datasets into an analysis-ready view while
preserving the original source files.
2. Calculate key sales, order, customer, product, and operational
metrics.
3. Identify trends and patterns across time, products, customer
segments, and locations.
4. Present findings through visualizations and interactive dashboard
filters.
5. Translate the findings into practical business recommendations.

## Scope and Business Context

The analysis focuses on retail/e-commerce performance. It includes
product-level sales, order-level metrics, customer segmentation,
category and geographic comparisons, payment methods/statuses, estimated
product profit, discounts, shipment information, cancellations, and
return requests.

The analysis is limited to the fields and records available in the
supplied CSV files. Any missing, inconsistent, or unavailable source
information should be documented in the notebook rather than assumed.

## Repository Contents

Recommended repository structure:
Retail-Capstone-Project/
├── README.md
├── Executive Summary.txt
├── One-Page Insights Summary.docx
├── YourNotebook.ipynb
├── app.py
├── data/
│   ├── cleaned\_dcustomers.csv
│   ├── cleaned\_dproducts.csv
│   ├── cleaned\_forders.csv
│   ├── cleaned\_forder\_items.csv
│   ├── cleaned\_fpayments.csv
│   ├── cleaned\_fshipments.csv
│   └── cleaned\_freturns.csv
└── charts/
    ├── 01\_executive.png
    ├── 02\_sales.png
    ├── 03\_products.png
    ├── 04\_customers.png
    ├── 05\_profit\_and\_discounts.png
    ├── 06\_payments.png
    └── 07\_logistics\_and\_returns.png
Data Analysis \& Methodology

### Data sources and relationships

The project uses these seven tables:

\---

Dataset                             Analytical purpose

\---

Customers                           Customer attributes, region, city,
and loyalty information

Products                            Product name, brand, category, unit
cost, and catalog price

Orders                              Order date/time, customer, order
status, sales channel, discount,
and shipping fee

Order Items                         Product, quantity, and unit price
at purchase

Payments                            Payment method, payment status,
payment date, and amount paid

Shipments                           Courier, shipment status, ship
date, and delivery date

Returns                             Return request date, reason, refund
indicator, and refund amount
---

The key relationships are based on customer ID, product ID, and order
ID. Order items provide the product-level transaction detail. Payments,
shipments, and returns may contain multiple records for one order, so
their relationship to orders should be handled carefully to avoid
multiplying sales values during joins.

### Key metrics and calculations

\---

Metric                              Calculation / definition

\---

Gross Revenue                       Sum of quantity × unit price at
purchase

Net Revenue                         Gross revenue after applying the
order discount

Total Orders                        Count of distinct fulfilled order
IDs

Average Order Value (AOV)           Net item sales per order, averaged
across distinct fulfilled orders

Monthly Revenue                     Revenue grouped by order month

Revenue by Product                  Gross revenue grouped by product

Revenue by Category                 Gross revenue grouped by product
category

Revenue by Region / City            Gross revenue grouped by customer
location

Estimated Product Cost              Quantity × product unit cost

Estimated Gross Profit              Net sales less estimated product
cost

Repeat Customer Rate                Repeat customers divided by
customers in the selected analysis
population

Payment Activity                    Distinct orders grouped by payment
method and payment status

Return Requests                     Distinct return IDs, analyzed using
return-request date

Cancellations                       Distinct cancelled orders, analyzed
using order date
---

### Filters and analytical techniques

The Streamlit dashboard provides interactive filters for:

* Month
* Region
* Sales Channel
* Product Category

The analysis uses grouping and aggregation, joins across related tables,
time-based trend analysis, ranking, customer segmentation, and
comparative visualizations. Dashboard charts should respond to the
selected filters.

### Order and customer definitions

The dashboard's sales analysis defines fulfilled sales as orders with a
status of **Completed** or **Shipped**. Confirm that these status values
match the source CSV values.

For customer segmentation, the dashboard uses the customer's
fulfilled-order history. When all months are selected, repeat customers
are those with at least two fulfilled orders, while single-order
customers have one. When a single month is selected, new customers are
those whose first fulfilled purchase occurred in that month; repeat
customers purchased before that month.

#### Data Analysis \& Methodology:

###### The analysis was conducted using Python, Pandas, Jupyter Notebook, and Streamlit to examine seven related retail/e-commerce datasets. The datasets were loaded and connected using relevant identifiers such as Customer ID, Product ID, and Order ID to support consolidated analysis.

###### The following key metrics and calculations were applied:

###### •	Total Gross Revenue: Sum of sales before discounts.

###### •	Net Revenue: Gross revenue less applicable discounts.

###### •	Total Orders: Count of distinct fulfilled orders.

###### •	Average Order Value (AOV): Net revenue divided by the number of fulfilled orders.

###### •	Monthly Revenue: Revenue grouped by month to identify sales trends.

###### •	Product and Category Performance: Revenue aggregated by product and product category.

###### •	Regional Performance: Revenue analyzed by region and city.

###### •	Repeat Customer Rate: Percentage of customers with two or more orders.

###### Interactive filters for Month, Region, Sales Channel, and Product Category were incorporated into the Streamlit dashboard to allow users to explore specific business segments.

###### Various analytical techniques, including data aggregation, table relationships, grouping, ranking, customer segmentation, and trend analysis, were applied to transform the datasets into meaningful business findings.

#### Key Takeaways

The analysis revealed several important findings about the business:

•	Total gross revenue reached ₱5,402,891.30, while net revenue amounted to ₱4,997,969.35.

•	The business recorded 11,658 fulfilled orders, with an average order value of ₱428.72.

•	August recorded revenue of ₱239,638.

•	Kid Joy was the top-performing product, generating ₱29,398 in revenue.

•	Toys was the leading product category, contributing ₱750,760.

•	Region III generated the highest regional revenue at ₱950,979.

•	Olongapo contributed ₱349,777 in city-level revenue.

•	Repeat customers accounted for 74.9% of the customer base, indicating strong repeat purchasing activity.

## Business Insights

1\. Sales Performance: The business generated ₱5.4 million in gross revenue from 11,658 fulfilled orders. This demonstrates an established sales base and provides opportunities to improve revenue through targeted promotions and sales strategies.

2\. Product and Regional Performance: Toys generated the highest category revenue at ₱750,760, while Region III contributed ₱950,979. This highlights the importance of popular product categories and strong-performing locations in driving business revenue.

3\. Customer Retention: The repeat customer rate reached 74.9%, indicating that a significant portion of customers made multiple purchases. Maintaining customer satisfaction and strengthening loyalty programs can help sustain repeat purchases and long-term revenue growth.

## Summary

The project analyzed seven retail/e-commerce datasets to evaluate sales performance, product contribution, customer behavior, and regional performance. The business generated ₱5,402,891.30 in gross revenue, with Toys identified as the leading product category and Region III as the highest-performing region. Additionally, the 74.9% repeat customer rate highlights the importance of customer retention. The interactive dashboard provides a consolidated view of business performance and supports further analysis through dynamic filters and visualizations.Conclusions

Write the final conclusions after reviewing the validated results. The
conclusions should directly answer the project objectives and summarize
what the analysis demonstrates about revenue performance, customer
behavior, product contribution, geographic performance, and operational
activity. Conclusions should not introduce new claims that were not
established in the analysis.

#### CONCLUSIONS

Based on the analysis, the business demonstrates strong revenue contribution from its leading product categories and geographic markets. The high repeat customer rate also suggests positive customer purchasing activity. The findings emphasize the importance of monitoring sales performance, maintaining popular product availability, strengthening customer relationships, and continuously evaluating business operations. Overall, the dashboard provides useful insights that can support informed and data-driven business decisions.

## Recommendations

Use the final results to prioritize practical actions. Potential
recommendation areas include:

1. **Product and inventory planning:** Review stock availability for
products and categories with consistently high sales contribution.
2. **Customer retention:** Develop relevant loyalty offers or follow-up
campaigns if the analysis shows an opportunity to increase repeat
purchasing.
3. **Regional sales planning:** Investigate high- and low-performing
regions/cities and adapt marketing or distribution plans based on
local performance.
4. **Pricing and discounts:** Evaluate whether discount levels are
associated with meaningful sales gains while monitoring estimated
gross profit.
5. **Payment experience:** Review payment methods and failed or pending
transactions to identify possible payment-friction points.
6. **Delivery and returns:** Investigate recurring courier, delivery,
cancellation, or return patterns and prioritize operational
improvements.

Keep only recommendations supported by the completed analysis, and
connect each recommendation to a specific finding.

## Tools Used

* Python
* Jupyter Notebook
* Pandas
* Plotly
* Streamlit
* GitHub

