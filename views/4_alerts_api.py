import streamlit as st
import lancedb
import pandas as pd
import json

st.title("🚨 Operational Alerts & ERP Integration Bridge")
st.caption("Real-time anomaly detection and webhook/API payload generator powered by LATTICE_AI.")

DB_PATH = "data/sample-lancedb"

@st.cache_resource
def get_db():
    return lancedb.connect(DB_PATH)

db = get_db()

if "vendor_docs" not in db.table_names():
    st.warning("⚠️ No database table found (`vendor_docs`). Please go to **Data Hub** and seed records first.")
else:
    table = db.open_table("vendor_docs")
    df = table.search("").limit(1000).to_pandas()

    if not df.empty and "text" in df.columns:
        # Explicitly ensure Series string accessor
        text_series = pd.Series(df["text"]).astype(str)

        # Safe Regex Extractions
        df["Shipment_ID"] = text_series.str.extract(r'Shipment_ID:\s*([^\s|]+)')
        df["Tracking_ID"] = text_series.str.extract(r'Tracking:\s*([^\s|]+)')
        df["Location"] = text_series.str.extract(r'Location:\s*([^|]+)')[0].fillna("Unknown").str.strip()
        df["Status"] = text_series.str.extract(r'Status:\s*([^|]+)')[0].fillna("UNKNOWN").str.strip()
        
        extracted_cost = text_series.str.extract(r'Cost:\s*\$?(\d+\.?\d*)')[0]
        df["Cost"] = pd.to_numeric(extracted_cost, errors="coerce").fillna(0.0)

        # --- 1. AUTOMATED ANOMALY ALERTS ---
        st.subheader("⚠️ Active System Anomalies")

        max_cost = float(df["Cost"].max()) if not df.empty and df["Cost"].max() > 0 else 10000.0
     high_value_threshold = st.slider(
    "High Financial Risk Threshold ($)", 
    min_value=100, 
    max_value=int(max_cost), 
    value=min(1100, int(max_cost)), 
    step=250
)

        high_risk_df = df[df["Cost"] >= high_value_threshold]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("High-Risk Exposure Records", len(high_risk_df))
        with col2:
            st.metric("Total High-Risk Capital ($)", f"${high_risk_df['Cost'].sum():,.2f}")

        if not high_risk_df.empty:
            for _, row in high_risk_df.iterrows():
                st.error(f"🚨 **ANOMALY DETECTED**: {row['Shipment_ID']} ({row['Tracking_ID']}) at **{row['Location']}** — Capital Exposure: **${row['Cost']:,.2f}**")
        else:
            st.success("✅ No high-risk anomalies detected above current threshold.")

        st.divider()

        # --- 2. REST / WEBHOOK PAYLOAD GENERATOR ---
        st.subheader("🔌 ERP Integration / Webhook Bridge (SAP / Oracle)")
        st.write("Export live telemetry payloads directly to external ERP systems or automated dispatch queues.")

        valid_ids = df["Shipment_ID"].dropna().unique()
        if len(valid_ids) > 0:
            selected_id = st.selectbox("Select Shipment Record to Construct Payload:", valid_ids)
            target_row = df[df["Shipment_ID"] == selected_id].iloc[0]

            payload = {
                "engine": "LATTICE_AI_Ultra_Hybrid_v1.6",
                "event_type": "TELEMETRY_ALERT_DISPATCH",
                "shipment_id": str(target_row["Shipment_ID"]),
                "tracking_number": str(target_row["Tracking_ID"]),
                "location_grid": str(target_row["Location"]),
                "status": str(target_row["Status"]),
                "financial_risk_usd": float(target_row["Cost"]),
                "raw_log_text": str(target_row["text"])
            }

            st.markdown("##### Generated JSON Payload:")
            st.code(json.dumps(payload, indent=4), language="json")

            st.download_button(
                label="📥 Download Webhook Payload (JSON)",
                data=json.dumps(payload, indent=4),
                file_name=f"payload_{selected_id}.json",
                mime="application/json"
            )