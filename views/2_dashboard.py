import streamlit as st
import pandas as pd
import numpy as np

st.title("📊 Analytics Dashboard")
st.write("Track sales performance, customer metrics, and revenue trends in real-time.")

# --- DUMMY DATA GENERATION ---
@st.cache_data
def load_data():
    np.random.seed(42)
    dates = pd.date_range(start="2026-01-01", periods=90, freq="D")
    data = pd.DataFrame({
        "Date": dates,
        "Category": np.random.choice(["Electronics", "Clothing", "Home & Kitchen", "Books"], size=90),
        "Sales": np.random.randint(100, 1000, size=90),
        "Units Sold": np.random.randint(1, 20, size=90),
        "Region": np.random.choice(["North", "South", "East", "West"], size=90)
    })
    return data

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Dashboard")

selected_category = st.sidebar.multiselect(
    "Select Category:",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

selected_region = st.sidebar.multiselect(
    "Select Region:",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

# Apply filters
filtered_df = df[
    (df["Category"].isin(selected_category)) & 
    (df["Region"].isin(selected_region))
]

# --- KPI METRICS ---
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

total_sales = filtered_df["Sales"].sum()
total_units = filtered_df["Units Sold"].sum()
avg_order_val = filtered_df["Sales"].mean() if len(filtered_df) > 0 else 0
active_regions = len(filtered_df["Region"].unique())

col1.metric(label="Total Revenue", value=f"${total_sales:,.2f}", delta="+8.4%")
col2.metric(label="Units Sold", value=f"{total_units:,}", delta="+12%")
col3.metric(label="Avg Order Value", value=f"${avg_order_val:,.2f}", delta="-2.1%")
col4.metric(label="Active Regions", value=f"{active_regions}")

st.divider()

# --- CHARTS SECTION ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Sales Trend Over Time")
    if not filtered_df.empty:
        # Group sales by date for the line chart
        daily_sales = filtered_df.groupby("Date")["Sales"].sum().reset_index()
        st.line_chart(daily_sales, x="Date", y="Sales", color="#1f77b4")
    else:
        st.info("No data matches current filters.")

with col_chart2:
    st.subheader("Sales by Category")
    if not filtered_df.empty:
        # Group sales by Category for the bar chart
        cat_sales = filtered_df.groupby("Category")["Sales"].sum().reset_index()
        st.bar_chart(cat_sales, x="Category", y="Sales")
    else:
        st.info("No data matches current filters.")

st.divider()

# --- INTERACTIVE DATA TABLE ---
st.subheader("Detailed Transaction Data")

# Allow user to download filtered data as CSV
csv_data = filtered_df.to_csv(index=False).encode('utf-8')

col_tbl1, col_tbl2 = st.columns([3, 1])
with col_tbl1:
    st.caption(f"Showing {len(filtered_df)} records")
with col_tbl2:
    st.download_button(
        label="📥 Export to CSV",
        data=csv_data,
        file_name="sales_report.csv",
        mime="text/csv"
    )

# Interactive data frame table with sorting and column formatting
st.dataframe(
    filtered_df,
    column_config={
        "Date": st.column_config.DateColumn("Transaction Date", format="YYYY-MM-DD"),
        "Sales": st.column_config.NumberColumn("Revenue ($)", format="$%d"),
        "Units Sold": st.column_config.NumberColumn("Units", format="%d"),
    },
    use_container_width=True,
    hide_index=True
)