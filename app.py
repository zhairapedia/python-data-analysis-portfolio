from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# RETAIL / E-COMMERCE CAPSTONE DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Retail Sales & Customer Insights",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Retail Sales & Customer Insights Dashboard")
st.caption("Sales performance, products, customers, payments, deliveries and returns")

# Folder containing the seven CSV files
DATA_DIR = Path(r"C:\PythonCapstoneProject\data")

FILES = {
    "customers": ["cleaned_dcustomers.csv"],
    "products": ["cleaned_dproducts.csv"],
    # Alternate spellings are included in case the files were saved as
    # cleaned_folders / cleaned_folder_items in Windows.
    "orders": ["cleaned_forders.csv", "cleaned_folders.csv"],
    "items": ["cleaned_forder_items.csv", "cleaned_folder_items.csv"],
    "payments": ["cleaned_fpayments.csv"],
    "shipments": ["cleaned_fshipments.csv"],
    "returns": ["cleaned_freturns.csv"],
}


def peso(value):
    return f"₱{value:,.2f}"


@st.cache_data
def load_data(data_dir):
    """Load source CSV files as provided; do not clean or modify source rows."""
    folder = Path(data_dir)
    tables = {}
    for key, filenames in FILES.items():
        matching_path = next((folder / name for name in filenames if (folder / name).exists()), None)
        if matching_path is None:
            expected_names = " or ".join(filenames)
            raise FileNotFoundError(f"Cannot find {expected_names} inside {folder}")
        tables[key] = pd.read_csv(matching_path)
    return tables


def make_analysis_tables(tables):
    """
    Prepare analysis views only:
    - parse date columns for time filters/charts
    - calculate line revenue
    - aggregate one-to-many tables before joining to avoid multiplying sales
    Source CSV data is not overwritten or cleaned.
    """
    customers = tables["customers"].copy()
    products = tables["products"].copy()

    # Use the region label exactly as it appears in the source CSV.
    # Prefer region_code (for example, "Region XIII - CARAGA") over
    # region_name (which may contain only "Caraga"). Fall back only when
    # the preferred source column is not present.
    normalized_customer_headers = {
        str(column).strip().lower().replace(" ", "_"): column
        for column in customers.columns
    }
    region_source_column = next(
        (normalized_customer_headers[column]
         for column in ["region_code", "region", "region_name"]
         if column in normalized_customer_headers),
        None,
    )
    if region_source_column is None:
        raise ValueError(
            "The customers CSV must contain a region_code, region_name, or region column. "
            f"Available columns: {list(customers.columns)}"
        )
    customers["region_display"] = customers[region_source_column]

    customer_merge_columns = ["customer_id", "region_display", "city", "loyalty_tier"]
    # Keep the original region_name too when it exists, for source-data visibility.
    if "region_name" in customers.columns:
        customer_merge_columns.append("region_name")
    orders = tables["orders"].copy()
    items = tables["items"].copy()
    payments = tables["payments"].copy()
    shipments = tables["shipments"].copy()
    returns = tables["returns"].copy()

    # Analysis date field
    orders["order_date"] = pd.to_datetime(orders["order_datetime"], dayfirst=True, errors="coerce")
    orders["month"] = orders["order_date"].dt.to_period("M").astype("string")

    # Numeric fields used in calculations (values should already be numeric in the CSVs)
    items["quantity"] = pd.to_numeric(items["quantity"], errors="coerce")
    items["purchase_unit_price"] = pd.to_numeric(items["unit_price_at_purchase"], errors="coerce")
    orders["discount_pct"] = pd.to_numeric(orders["discount_pct"], errors="coerce")
    products["unit_cost_num"] = pd.to_numeric(products["unit_cost"], errors="coerce")

    # Aggregate one-to-many tables to one row per order before joining.
    payment_by_order = payments.groupby("order_id", as_index=False).agg(
        payment_amount=("amount_paid", "sum"),
        payment_methods=("payment_method", lambda x: ", ".join(x.dropna().astype(str).unique())),
        payment_statuses=("payment_status", lambda x: ", ".join(x.dropna().astype(str).unique())),
    )

    shipments["delivered_date_analysis"] = pd.to_datetime(
        shipments["delivered_date"], dayfirst=True, errors="coerce"
    )
    shipment_by_order = shipments.groupby("order_id", as_index=False).agg(
        couriers=("courier", lambda x: ", ".join(x.dropna().astype(str).unique())),
        shipment_statuses=("shipment_status", lambda x: ", ".join(x.dropna().astype(str).unique())),
        delivered_date=("delivered_date_analysis", "max"),
    )

    returns["return_date_analysis"] = pd.to_datetime(
        returns["return_request_date"], dayfirst=True, errors="coerce"
    )
    returns_by_order = returns.groupby("order_id", as_index=False).agg(
        return_records=("return_id", "nunique"),
        return_date=("return_date_analysis", "min"),
        return_reasons=("reason", lambda x: ", ".join(x.dropna().astype(str).unique())),
        refund_flags=("refunded_flag", lambda x: ", ".join(x.dropna().astype(str).unique())),
        refund_amount=("refund_amount", "sum"),
    )

    fact = (
        items.merge(orders, on="order_id", how="left")
        .merge(
            products[["product_id", "product_name", "brand", "category", "unit_cost_num"]],
            on="product_id", how="left"
        )
        .merge(
            customers[customer_merge_columns],
            on="customer_id", how="left"
        )
        .merge(payment_by_order, on="order_id", how="left")
        .merge(shipment_by_order, on="order_id", how="left")
        .merge(returns_by_order, on="order_id", how="left")
    )

    fact["gross_sales"] = fact["quantity"] * fact["purchase_unit_price"]
    fact["net_sales"] = fact["gross_sales"] * (1 - fact["discount_pct"].fillna(0))
    fact["estimated_gross_profit"] = (
        fact["net_sales"] - (fact["quantity"] * fact["unit_cost_num"])
    )
    fact["month"] = fact["order_date"].dt.to_period("M").astype("string")

    # Use the same fulfilled-sales definition as the original dashboard.
    fulfilled = fact[
        fact["order_status"].astype("string").str.lower().isin(["completed", "shipped"])
    ].copy()

    # Order-level analysis table (one row per order)
    order_analysis = orders.merge(
        customers[customer_merge_columns],
        on="customer_id", how="left"
    )
    order_analysis["order_status_clean"] = order_analysis["order_status"].astype("string").str.lower()

    # First fulfilled purchase is based on all fulfilled order history.
    first_purchase = fulfilled.groupby("customer_id")["order_date"].min()
    fulfilled = fulfilled.merge(
        first_purchase.rename("first_fulfilled_purchase"),
        on="customer_id", how="left"
    )

    return fact, fulfilled, order_analysis, returns


def apply_filters(df, month, region, channel, category):
    result = df.copy()
    if month != "All":
        result = result[result["month"] == month]
    if region != "All":
        result = result[result["region_display"] == region]
    if channel != "All":
        result = result[result["sales_channel"] == channel]
    if category != "All":
        result = result[result["category"] == category]
    return result


# -------------------- LOAD DATA --------------------
try:
    source_tables = load_data(str(DATA_DIR))
    fact, fulfilled, order_analysis, source_returns = make_analysis_tables(source_tables)
except Exception as exc:
    st.error("The dashboard could not load the CSV files.")
    st.exception(exc)
    st.info(
        "Check that all seven CSV files are inside C:\\PythonCapstoneProject\\data "
        "and that the filenames match the FILES list near the top of app.py."
    )
    st.stop()

if fulfilled.empty:
    st.warning("No rows with Completed or Shipped order status were found.")
    st.stop()

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("Dashboard Filters")

months = ["All"] + sorted(fulfilled["month"].dropna().astype(str).unique().tolist())
regions = ["All"] + sorted(fulfilled["region_display"].dropna().astype(str).unique().tolist())
channels = ["All"] + sorted(fulfilled["sales_channel"].dropna().astype(str).unique().tolist())
categories = ["All"] + sorted(fulfilled["category"].dropna().astype(str).unique().tolist())

selected_month = st.sidebar.selectbox("Month", months)
selected_region = st.sidebar.selectbox("Region", regions)
selected_channel = st.sidebar.selectbox("Sales Channel", channels)
selected_category = st.sidebar.selectbox("Product Category", categories)

filtered = apply_filters(
    fulfilled, selected_month, selected_region, selected_channel, selected_category
)
fact_filtered = apply_filters(
    fact, selected_month, selected_region, selected_channel, selected_category
)

if filtered.empty:
    st.warning("No fulfilled sales match the selected filters. Change the filters.")
    st.stop()

# -------------------- KPIs --------------------
gross_revenue = filtered["gross_sales"].sum()
net_revenue = filtered["net_sales"].sum()
total_orders = filtered["order_id"].nunique()
order_values = filtered.groupby("order_id", as_index=False).agg(order_value=("net_sales", "sum"))
aov = order_values["order_value"].mean() if not order_values.empty else 0

category_revenue = filtered.groupby("category")["gross_sales"].sum()
top_category = category_revenue.idxmax() if not category_revenue.empty else "N/A"

customer_orders = filtered.groupby("customer_id", as_index=False).agg(
    first_fulfilled_purchase=("first_fulfilled_purchase", "min")
)
lifetime_counts = fulfilled.groupby("customer_id")["order_id"].nunique()
customer_orders = customer_orders.merge(
    lifetime_counts.rename("lifetime_orders"), on="customer_id", how="left"
)

if selected_month == "All":
    customer_orders["customer_type"] = customer_orders["lifetime_orders"].apply(
        lambda n: "Repeat (2+ orders)" if n >= 2 else "Single-order (1 order)"
    )
    customer_definition = "All months: repeat customers have at least two fulfilled orders in the full dataset."
else:
    selected_period = pd.Period(selected_month, freq="M")
    customer_orders["customer_type"] = customer_orders["first_fulfilled_purchase"].apply(
        lambda d: "New customer"
        if pd.notna(d) and d.to_period("M") == selected_period
        else "Repeat customer"
    )
    customer_definition = "Selected month: new customers made their first fulfilled purchase in that month."

customer_type_counts = customer_orders.groupby("customer_type")["customer_id"].nunique().reset_index(name="customers")
customer_count = customer_orders["customer_id"].nunique()
repeat_count = customer_orders[
    customer_orders["customer_type"].isin(["Repeat customer", "Repeat (2+ orders)"])
]["customer_id"].nunique()
repeat_rate = repeat_count / customer_count * 100 if customer_count else 0

# -------------------- NAVIGATION --------------------
st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #dedfe3; background: #fbfbfc; padding: 0 8px; flex-wrap: nowrap; overflow-x: auto; }
.stTabs [data-baseweb="tab"] { height: 54px; padding: 0 2px; background: transparent; border: none; color: #45464d; font-size: 16px; white-space: nowrap; }
.stTabs [aria-selected="true"] { color: #f05260 !important; border-bottom: 3px solid #f05260 !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "Executive", "Sales", "Products", "Customers", "Profit & Discounts",
    "Payments", "Logistics & Returns", "Data Explorer", "Report & Export"
])

monthly_sales = filtered.groupby("month", as_index=False).agg(
    gross_sales=("gross_sales", "sum"), net_sales=("net_sales", "sum")
).sort_values("month")

# -------------------- SALES --------------------
with tabs[1]:
    st.subheader("Sales Trend")
    fig = px.line(
        monthly_sales, x="month", y="gross_sales", markers=True,
        title="Monthly Gross Sales",
        labels={"month": "Month", "gross_sales": "Gross Sales (PHP)"}
    )
    fig.update_layout(yaxis_tickprefix="₱", yaxis_tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

# -------------------- PRODUCTS --------------------
with tabs[2]:
    c1, c2 = st.columns(2)
    top_products = filtered.groupby("product_name", as_index=False)["gross_sales"].sum().nlargest(10, "gross_sales").sort_values("gross_sales")
    fig_products = px.bar(top_products, x="gross_sales", y="product_name", orientation="h",
                          title="Top 10 Products by Revenue",
                          labels={"gross_sales": "Gross Sales (PHP)", "product_name": "Product"})
    fig_products.update_layout(xaxis_tickprefix="₱", xaxis_tickformat=",.0f")
    c1.plotly_chart(fig_products, use_container_width=True)

    category_sales = filtered.groupby("category", as_index=False)["gross_sales"].sum().sort_values("gross_sales")
    fig_category = px.bar(category_sales, x="gross_sales", y="category", orientation="h",
                          title="Revenue by Product Category",
                          labels={"gross_sales": "Gross Sales (PHP)", "category": "Category"})
    fig_category.update_layout(xaxis_tickprefix="₱", xaxis_tickformat=",.0f")
    c2.plotly_chart(fig_category, use_container_width=True)

    c3, c4 = st.columns(2)
    region_sales = filtered.groupby("region_display", as_index=False)["gross_sales"].sum().sort_values("gross_sales")
    fig_region = px.bar(region_sales, x="gross_sales", y="region_display", orientation="h",
                        title="Revenue by Region",
                        labels={"gross_sales": "Gross Sales (PHP)", "region_display": "Region"})
    fig_region.update_layout(xaxis_tickprefix="₱", xaxis_tickformat=",.0f")
    c3.plotly_chart(fig_region, use_container_width=True)

    city_sales = filtered.groupby("city", as_index=False)["gross_sales"].sum().nlargest(10, "gross_sales").sort_values("gross_sales")
    fig_city = px.bar(city_sales, x="gross_sales", y="city", orientation="h",
                      title="Top 10 Cities by Revenue",
                      labels={"gross_sales": "Gross Sales (PHP)", "city": "City"})
    fig_city.update_layout(xaxis_tickprefix="₱", xaxis_tickformat=",.0f")
    c4.plotly_chart(fig_city, use_container_width=True)

# -------------------- CUSTOMERS --------------------
with tabs[3]:
    st.subheader("Customer Insights")
    st.caption(customer_definition)
    c1, c2 = st.columns([1, 2])
    fig_customer = px.pie(customer_type_counts, names="customer_type", values="customers",
                          hole=0.55, title="New vs. Repeat / Single-Order Customers")
    c1.plotly_chart(fig_customer, use_container_width=True)
    c2.metric("Customers in Selection", f"{customer_count:,}")
    c2.metric("Repeat Customers", f"{repeat_count:,}")
    c2.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")

# -------------------- PROFIT & DISCOUNTS --------------------
with tabs[4]:
    st.subheader("Order Value Distribution")
    fig_aov = px.histogram(order_values, x="order_value", nbins=30,
                           title="Distribution of Net Order Values",
                           labels={"order_value": "Net Order Value (PHP)"})
    fig_aov.update_layout(xaxis_tickprefix="₱", xaxis_tickformat=",.0f", yaxis_title="Number of Orders")
    st.plotly_chart(fig_aov, use_container_width=True)

    st.subheader("Estimated Profit by Product Category")
    profit_by_category = filtered.groupby("category", as_index=False).agg(
        estimated_gross_profit=("estimated_gross_profit", "sum")
    ).sort_values("estimated_gross_profit")
    fig_profit = px.bar(profit_by_category, x="estimated_gross_profit", y="category",
                        orientation="h", title="Estimated Gross Profit by Category",
                        labels={"estimated_gross_profit": "Estimated Gross Profit (PHP)", "category": "Category"})
    fig_profit.update_layout(xaxis_tickprefix="₱", xaxis_tickformat=",.0f")
    st.plotly_chart(fig_profit, use_container_width=True)

    st.subheader("Discount Overview")
    discount_view = filtered.copy()
    discount_view["discount_label"] = (discount_view["discount_pct"].fillna(0) * 100).round().astype(int).astype(str) + "%"
    discount_sales = discount_view.groupby("discount_label", as_index=False).agg(
        net_sales=("net_sales", "sum"), orders=("order_id", "nunique")
    )
    fig_discount = px.bar(discount_sales, x="discount_label", y="net_sales",
                          title="Net Sales by Discount Level",
                          labels={"discount_label": "Discount", "net_sales": "Net Sales (PHP)"})
    fig_discount.update_layout(yaxis_tickprefix="₱", yaxis_tickformat=",.0f")
    st.plotly_chart(fig_discount, use_container_width=True)

# -------------------- PAYMENTS --------------------
with tabs[5]:
    st.subheader("Payment Insights")
    payment_view = filtered.copy()
    if not payment_view.empty and "payment_methods" in payment_view.columns:
        payment_chart = payment_view.groupby(["payment_methods", "payment_statuses"])["order_id"].nunique().reset_index(name="Orders")

        # Use clearly contrasting colors while keeping the original status labels
        # exactly as they appear in the CSV data.
        payment_status_palette = {
            "paid": "#16A34A",       # Green
            "pending": "#F59E0B",    # Amber
            "failed": "#DC2626",     # Red
            "refunded": "#7C3AED",   # Purple
        }
        payment_status_colors = {
            status: payment_status_palette.get(str(status).strip().lower(), "#64748B")
            for status in payment_chart["payment_statuses"].dropna().unique()
        }

        fig_payment = px.bar(
            payment_chart,
            x="payment_methods",
            y="Orders",
            color="payment_statuses",
            barmode="stack",
            title="Orders by Payment Method and Payment Status",
            labels={
                "payment_methods": "Payment Method",
                "payment_statuses": "Payment Status"
            },
            color_discrete_map=payment_status_colors
        )
        fig_payment.update_layout(
            legend_title_text="Payment Status",
            bargap=0.25
        )
        st.plotly_chart(fig_payment, use_container_width=True)
    else:
        st.info("No payment information is available for this selection.")

# -------------------- LOGISTICS & RETURNS --------------------
with tabs[6]:
    st.subheader("Returns and Cancellations")
    selected_order_ids = set(fact_filtered["order_id"].dropna().unique())

    cancelled = order_analysis[
        order_analysis["order_status_clean"].str.contains("cancel", na=False)
    ].copy()
    cancelled = cancelled[cancelled["order_id"].isin(selected_order_ids)]
    if selected_month != "All":
        cancelled = cancelled[cancelled["month"] == selected_month]
    if selected_region != "All":
        cancelled = cancelled[cancelled["region_display"] == selected_region]
    if selected_channel != "All":
        cancelled = cancelled[cancelled["sales_channel"] == selected_channel]
    cancelled_monthly = cancelled.groupby("month")["order_id"].nunique().rename("Cancelled orders")

    returns_view = source_returns.copy()
    returns_view["return_month"] = pd.to_datetime(
        returns_view["return_request_date"], dayfirst=True, errors="coerce"
    ).dt.to_period("M").astype("string")
    order_filter = order_analysis[["order_id", "region_display", "sales_channel", "month"]]
    returns_view = returns_view.merge(order_filter, on="order_id", how="left")
    returns_view = returns_view[returns_view["order_id"].isin(selected_order_ids)]
    if selected_month != "All":
        returns_view = returns_view[returns_view["month"] == selected_month]
    if selected_region != "All":
        returns_view = returns_view[returns_view["region_display"] == selected_region]
    if selected_channel != "All":
        returns_view = returns_view[returns_view["sales_channel"] == selected_channel]

    returned_monthly = returns_view.dropna(subset=["return_month"]).groupby("return_month")["return_id"].nunique().rename("Return requests")
    outcome_trend = pd.concat([cancelled_monthly, returned_monthly], axis=1).fillna(0).reset_index()
    if not outcome_trend.empty:
        outcome_trend = outcome_trend.rename(columns={"index": "month"})
        outcome_trend = outcome_trend.melt(id_vars="month", var_name="Order outcome", value_name="Number of records")
        fig_outcomes = px.line(outcome_trend, x="month", y="Number of records", color="Order outcome",
                               markers=True, title="Monthly Cancellations and Return Requests")
        st.plotly_chart(fig_outcomes, use_container_width=True)
    else:
        st.info("No return requests or cancellations are available for the selected filters.")

    st.caption("Cancellation counts use order date. Return counts use return-request date.")

    st.subheader("Shipping and Delivery Performance")
    if "couriers" in filtered.columns:
        courier_counts = filtered.groupby("couriers")["order_id"].nunique().sort_values(ascending=False).reset_index(name="Orders")
        fig_courier = px.bar(courier_counts, x="couriers", y="Orders",
                             title="Orders by Courier",
                             labels={"couriers": "Courier", "Orders": "Number of Orders"})
        st.plotly_chart(fig_courier, use_container_width=True)
        st.metric("Fulfilled item rows with a recorded delivery date", f"{filtered['delivered_date'].notna().sum():,}")

# -------------------- DATA EXPLORER --------------------
with tabs[7]:
    st.subheader("Filtered Sales Data")
    display_cols = [
        "order_id", "order_date", "customer_id", "product_id", "product_name",
        "category", "quantity", "purchase_unit_price", "gross_sales", "discount_pct",
        "net_sales", "region_display", "region_name", "city", "sales_channel", "payment_methods",
        "payment_statuses", "couriers", "shipment_statuses", "return_reasons",
        "refund_flags", "refund_amount"
    ]
    display_cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

# -------------------- REPORT & EXPORT --------------------
with tabs[8]:
    st.subheader("Export Reports")
    st.download_button(
        "Download filtered sales data (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_fulfilled_sales.csv",
        mime="text/csv"
    )
    st.subheader("Source CSV Files")
    for table_name, df in source_tables.items():
        st.write(f"**{table_name.title()}** — {len(df):,} rows × {len(df.columns):,} columns")
        with st.expander(f"Preview {table_name}"):
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)

# -------------------- EXECUTIVE DASHBOARD --------------------
with tabs[0]:
    st.subheader("Key Performance Indicators")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Gross Sales", peso(gross_revenue))
    k2.metric("Fulfilled Orders", f"{total_orders:,}")
    k3.metric("Average Order Value", peso(aov))
    k4.metric("Top Category", str(top_category))
    st.caption(
        f"Net sales after discounts: {peso(net_revenue)} | "
        f"Customers: {customer_count:,} | Repeat customer rate: {repeat_rate:.1f}%"
    )

    st.subheader("Key Business Insights")
    insights = []
    if len(monthly_sales) >= 2 and monthly_sales.iloc[0]["gross_sales"] != 0:
        change = (monthly_sales.iloc[-1]["gross_sales"] - monthly_sales.iloc[0]["gross_sales"]) / monthly_sales.iloc[0]["gross_sales"] * 100
        direction = "increased" if change >= 0 else "decreased"
        insights.append(f"Gross sales {direction} by {abs(change):.1f}% from {monthly_sales.iloc[0]['month']} to {monthly_sales.iloc[-1]['month']}.")
    if not category_revenue.empty:
        share = category_revenue.max() / gross_revenue * 100 if gross_revenue else 0
        insights.append(f"{top_category} is the leading category, contributing {share:.1f}% of gross revenue.")
    product_rank = filtered.groupby("product_name")["gross_sales"].sum().sort_values(ascending=False)
    if not product_rank.empty:
        insights.append(f"{product_rank.index[0]} is the top product by revenue, generating {peso(product_rank.iloc[0])}.")
    region_rank = filtered.groupby("region_display")["gross_sales"].sum().sort_values(ascending=False)
    if not region_rank.empty:
        insights.append(f"{region_rank.index[0]} leads regional sales with {region_rank.max() / gross_revenue * 100:.1f}% of gross revenue.")
    insights.append(f"Average order value is {peso(aov)} across fulfilled orders.")
    insights.append(f"{repeat_rate:.1f}% of customers in the selected data are classified as repeat customers.")
    for insight in insights[:8]:
        st.markdown(f"- {insight}")

    st.subheader("Business Recommendations")
    if not category_revenue.empty:
        st.markdown(f"1. Maintain suitable stock levels and product visibility for **{top_category}**, the leading revenue category.")
    if repeat_rate < 30:
        st.markdown("2. Strengthen repeat-purchase campaigns through loyalty rewards, personalized offers and post-purchase messages.")
    else:
        st.markdown("2. Build on repeat purchasing with tier-based loyalty rewards and relevant cross-sell offers.")

    st.caption("Use the sidebar filters to update the KPIs, charts, insights and recommendations.")
