import streamlit as st
import lancedb
import pandas as pd
import plotly.express as px

st.title("📊 Fleet Telemetry Analytics")
st.caption("High-level executive metrics, status distribution, and financial exposure across all ingested logs.")

DB_PATH = "data/sample-lancedb"

@st.cache_resource
def get_db():
    return lancedb.connect(DB_PATH)

db = get_db()

if "vendor_docs" not in db.table_names():
    st.warning("⚠️ No data found in database. Please go to **Data Hub** and seed or upload records first.")
else:
    table = db.open_table("vendor_docs")
    df = table.search("").limit(1000).to_pandas()

    if df.empty:
        st.info("Database table is empty.")
    else:
        # Parse structured details out of raw log text for charting
        df["Shipment_ID"] = df["text"].str.extract(r'Shipment_ID:\s*([^\s|]+)')
        df["Tracking_ID"] = df["text"].str.extract(r'Tracking:\s*([^\s|]+)')
        df["Location"] = df["text"].str.extract(r'Location:\s*([^|]+)')
        df["Status"] = df["text"].str.extract(r'Status:\s*([^|]+)')
        df["Cost"] = df["text"].str.extract(r'Cost:\s*\$?(\d+\.?\d*)')[0].astype(float)

        # Clean strings
        df["Location"] = df["Location"].str.strip().fillna("Unknown")
        df["Status"] = df["Status"].str.strip().fillna("UNKNOWN")
        df["Cost"] = df["Cost"].fillna(0.0)

        # Top Executive KPI Cards
        st.subheader("📈 Key Operational Metrics")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        kpi1.metric("Total Monitored Shipments", len(df))
        kpi2.metric("Total Financial Exposure", f"${df['Cost'].sum():,.2f}")
        kpi3.metric("Avg Cost per Shipment", f"${df['Cost'].mean():,.2f}")
        
        delivered_cnt = (df["Status"].str.upper() == "DELIVERED").sum()
        kpi4.metric("Delivery Rate", f"{(delivered_cnt / len(df) * 100):.1f}%")

        st.divider()

        # Visual Charts Section
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("📦 Shipments by Location")
            loc_fig = px.bar(
                df["Location"].value_counts().reset_index(),
                x="Location",
                y="count",
                labels={"count": "Shipment Count"},
                color="Location",
                title="Shipment Volume across Hubs & DCs"
            )
            st.plotly_chart(loc_fig, use_container_width=True)

        with c2:
            st.subheader("💰 Exposure Distribution by Hub")
            cost_fig = px.pie(
                df,
                names="Location",
                values="Cost",
                hole=0.4,
                title="Financial Value Breakdown by Location"
            )
            st.plotly_chart(cost_fig, use_container_width=True)

        st.divider()

        # Data Table View
        st.subheader("📋 Ingested Telemetry Master Table")
        st.dataframe(
            df[["Shipment_ID", "Tracking_ID", "Location", "Status", "Cost", "filename"]],
            use_container_width=True
        )