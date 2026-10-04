import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from src.config import WAREHOUSE_PATH

st.set_page_config(
    page_title="Smart Retail Analytics Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Connect to DuckDB warehouse
@st.cache_data
def load_data():
    con = duckdb.connect(WAREHOUSE_PATH, read_only=True)
    df_mart = con.execute("SELECT * FROM daily_store_performance").fetchdf()
    df_fact = con.execute("SELECT * FROM fact_sales").fetchdf()
    df_rejected = con.execute("SELECT * FROM rejected_sales_audit").fetchdf()
    con.close()
    return df_mart, df_fact, df_rejected

df_mart, df_fact, df_rejected = load_data()

# Header
st.title("🛒 Smart Retail Analytical Dashboard")
st.markdown("Real-time metrics sourced from the DuckDB Star-Schema Warehouse.")

# Sidebar Filters
st.sidebar.header("Filter Options")
stores = ["All Stores"] + sorted(df_mart["store_id"].unique().tolist())
selected_store = st.sidebar.selectbox("Select Store:", stores)

if selected_store != "All Stores":
    filtered_mart = df_mart[df_mart["store_id"] == selected_store]
    filtered_fact = df_fact[df_fact["store_id"] == selected_store]
else:
    filtered_mart = df_mart
    filtered_fact = df_fact

# KPI Summary Cards
col1, col2, col3, col4 = st.columns(4)

total_net = filtered_mart["net_revenue"].sum()
total_gross = filtered_mart["gross_sales"].sum()
total_orders = filtered_mart["total_orders"].sum()
avg_basket = filtered_mart["avg_basket_value"].mean()

col1.metric("Net Revenue", f"${total_net:,.2f}")
col2.metric("Gross Sales", f"${total_gross:,.2f}")
col3.metric("Total Orders", f"{int(total_orders):,}")
col4.metric("Avg Basket Value", f"${avg_basket:,.2f}")

st.markdown("---")

# Visual Charts: Store Breakdown & Revenue Trend
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Revenue by Store")
    store_rev = df_mart.groupby("store_id")["net_revenue"].sum().reset_index()
    fig_bar = px.bar(
        store_rev,
        x="store_id",
        y="net_revenue",
        labels={"store_id": "Store ID", "net_revenue": "Net Revenue ($)"},
        color="net_revenue",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with row1_col2:
    st.subheader("Daily Revenue Trend")
    trend = df_mart.groupby("date_key")["net_revenue"].sum().reset_index()
    trend["date_key"] = trend["date_key"].astype(str)
    fig_line = px.line(
        trend,
        x="date_key",
        y="net_revenue",
        labels={"date_key": "Date Key", "net_revenue": "Net Revenue ($)"},
        markers=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# Data Quality & Operational Insights
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Data Quality Audit (Rejected Records)")
    if not df_rejected.empty and "rejection_reason" in df_rejected.columns:
        reject_counts = df_rejected["rejection_reason"].value_counts().reset_index()
        reject_counts.columns = ["Reason", "Count"]
        fig_pie = px.pie(
            reject_counts,
            names="Reason",
            values="Count",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.success("No rejected records found or audit table empty.")

with row2_col2:
    st.subheader("Hourly Transaction Distribution")
    # Identify timestamp column dynamically from fact_sales
    time_col = None
    for candidate in ["transaction_time", "timestamp", "datetime", "created_at"]:
        if candidate in filtered_fact.columns:
            time_col = candidate
            break

    metric_col = "net_amount" if "net_amount" in filtered_fact.columns else filtered_fact.columns[0]

    if time_col is not None:
        fact_copy = filtered_fact.copy()
        fact_copy["hour"] = pd.to_datetime(fact_copy[time_col]).dt.hour
        hourly = fact_copy.groupby("hour")[metric_col].count().reset_index()
        hourly.columns = ["Hour of Day", "Transactions"]
        fig_hour = px.bar(
            hourly,
            x="Hour of Day",
            y="Transactions",
            color_discrete_sequence=["#2ca02c"]
        )
        st.plotly_chart(fig_hour, use_container_width=True)
    elif "hour" in filtered_fact.columns:
        hourly = filtered_fact.groupby("hour")[metric_col].count().reset_index()
        hourly.columns = ["Hour of Day", "Transactions"]
        fig_hour = px.bar(
            hourly,
            x="Hour of Day",
            y="Transactions",
            color_discrete_sequence=["#2ca02c"]
        )
        st.plotly_chart(fig_hour, use_container_width=True)
    else:
        st.info("No timestamp or hour column found in fact_sales.")

# Raw Mart Table View
st.markdown("---")
st.subheader("Daily Store Performance Mart Data")
st.dataframe(filtered_mart, use_container_width=True)