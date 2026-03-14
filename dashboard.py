import pandas as pd
import duckdb
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Supermarket Dashboard", layout="wide")

st.title("Supermarket Sales Dashboard")
st.markdown("Local dashboard powered by DuckDB")

# -----------------------------
# LOAD DATA
# -----------------------------
conn = duckdb.connect("warehouse.duckdb")
df = conn.execute("SELECT * FROM sales_data").fetchdf()
conn.close()

# -----------------------------
# CLEAN DATA
# -----------------------------
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

if "profit" not in df.columns and {"sales", "quantity", "cost_price"}.issubset(df.columns):
    df["profit"] = df["sales"] - (df["quantity"] * df["cost_price"])

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

if "city" in df.columns:
    city_options = ["All"] + sorted(df["city"].dropna().astype(str).unique().tolist())
    selected_city = st.sidebar.selectbox("Select City", city_options)
    if selected_city != "All":
        df = df[df["city"] == selected_city]

if "product_line" in df.columns:
    product_options = ["All"] + sorted(df["product_line"].dropna().astype(str).unique().tolist())
    selected_product = st.sidebar.selectbox("Select Product Line", product_options)
    if selected_product != "All":
        df = df[df["product_line"] == selected_product]

if "payment" in df.columns:
    payment_options = ["All"] + sorted(df["payment"].dropna().astype(str).unique().tolist())
    selected_payment = st.sidebar.selectbox("Select Payment Method", payment_options)
    if selected_payment != "All":
        df = df[df["payment"] == selected_payment]

# -----------------------------
# KPI METRICS
# -----------------------------
avg_sales = round(df["sales"].mean(), 2) if "sales" in df.columns and not df.empty else 0
avg_cost = round(df["cost_price"].mean(), 2) if "cost_price" in df.columns and not df.empty else 0
total_sales = round(df["sales"].sum(), 2) if "sales" in df.columns and not df.empty else 0
total_profit = round(df["profit"].sum(), 2) if "profit" in df.columns and not df.empty else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Average Sales", avg_sales)
k2.metric("Average Product Cost", avg_cost)
k3.metric("Total Sales", total_sales)
k4.metric("Total Profit", total_profit)

st.markdown("---")

# -----------------------------
# 1. BAR CHART
# -----------------------------
if {"product_line", "sales"}.issubset(df.columns) and not df.empty:
    sales_by_product = (
        df.groupby("product_line", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )

    fig_bar = px.bar(
        sales_by_product,
        x="product_line",
        y="sales",
        title="Total Sales by Product Line"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# 2. PIE CHART
# -----------------------------
if {"city", "sales"}.issubset(df.columns) and not df.empty:
    sales_by_city = (
        df.groupby("city", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )

    fig_pie = px.pie(
        sales_by_city,
        names="city",
        values="sales",
        title="Sales Distribution by City"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------
# 3. LINE CHART
# -----------------------------
if {"date", "sales"}.issubset(df.columns) and not df.empty:
    monthly_df = df.dropna(subset=["date"]).copy()
    monthly_df["month"] = monthly_df["date"].dt.to_period("M").astype(str)

    monthly_sales = (
        monthly_df.groupby("month", as_index=False)["sales"]
        .sum()
        .sort_values("month")
    )

    fig_line = px.line(
        monthly_sales,
        x="month",
        y="sales",
        markers=True,
        title="Monthly Sales Trend"
    )
    st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# 4. BOX PLOT
# -----------------------------
if {"product_line", "sales"}.issubset(df.columns) and not df.empty:
    fig_box = px.box(
        df,
        x="product_line",
        y="sales",
        title="Sales Distribution by Product Line"
    )
    st.plotly_chart(fig_box, use_container_width=True)

# -----------------------------
# 5. SCATTER PLOT
# -----------------------------
if {"cost_price", "profit", "product_line"}.issubset(df.columns) and not df.empty:
    fig_scatter = px.scatter(
        df,
        x="cost_price",
        y="profit",
        color="product_line",
        title="Cost vs Profit Analysis"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# -----------------------------
# 6. HISTOGRAM
# -----------------------------
if "sales" in df.columns and not df.empty:
    fig_hist = px.histogram(
        df,
        x="sales",
        nbins=30,
        title="Sales Frequency Distribution"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# -----------------------------
# 7. DONUT CHART
# -----------------------------
if {"payment", "sales"}.issubset(df.columns) and not df.empty:
    payment_sales = (
        df.groupby("payment", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )

    fig_donut = px.pie(
        payment_sales,
        names="payment",
        values="sales",
        hole=0.5,
        title="Sales by Payment Method"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# -----------------------------
# 8. AREA CHART
# -----------------------------
if {"date", "sales"}.issubset(df.columns) and not df.empty:
    daily_df = df.dropna(subset=["date"]).copy()
    daily_sales = (
        daily_df.groupby("date", as_index=False)["sales"]
        .sum()
        .sort_values("date")
    )

    fig_area = px.area(
        daily_sales,
        x="date",
        y="sales",
        title="Daily Sales Area Trend"
    )
    st.plotly_chart(fig_area, use_container_width=True)

# -----------------------------
# 9. PROFIT BAR CHART
# -----------------------------
if {"product_line", "profit"}.issubset(df.columns) and not df.empty:
    profit_by_product = (
        df.groupby("product_line", as_index=False)["profit"]
        .sum()
        .sort_values("profit", ascending=False)
    )

    fig_profit = px.bar(
        profit_by_product,
        x="product_line",
        y="profit",
        title="Total Profit by Product Line"
    )
    st.plotly_chart(fig_profit, use_container_width=True)

# -----------------------------
# 10. HEATMAP-LIKE CHART
# -----------------------------
if {"city", "product_line", "sales"}.issubset(df.columns) and not df.empty:
    pivot_df = df.pivot_table(
        index="city",
        columns="product_line",
        values="sales",
        aggfunc="sum",
        fill_value=0
    )

    heatmap_df = pivot_df.reset_index().melt(id_vars="city", var_name="product_line", value_name="sales")

    fig_heat = px.density_heatmap(
        heatmap_df,
        x="product_line",
        y="city",
        z="sales",
        title="Sales Heatmap: City vs Product Line"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# -----------------------------
# DATA PREVIEW
# -----------------------------
st.markdown("---")
st.subheader("Data Preview")
st.dataframe(df.head(20), use_container_width=True)
