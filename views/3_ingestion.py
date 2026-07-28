import streamlit as st
import lancedb
import pandas as pd
import os

st.title("📁 Data Hub & Ingestion Engine")
st.caption("Seed sample telemetry or upload custom spreadsheets for automated LATTICE_AI vector indexing.")

DB_PATH = "data/sample-lancedb"

@st.cache_resource
def get_db():
    os.makedirs(DB_PATH, exist_ok=True)
    return lancedb.connect(DB_PATH)

db = get_db()

# --- 1. SAMPLE DATA SEEDER ---
st.subheader("🌱 Sample Data Generator")
st.write("Populate LanceDB with mock multi-state logistics and carrier telemetry logs.")

sample_logs = [
    {"filename": "carrier_log_01.csv", "text": "Shipment_ID: SH-1092 | Tracking: TRK-8821 | Location: Dallas, TX | Status: IN TRANSIT | Cost: $1,250.00 | Notes: Temperature alert resolved at TX DC-1."},
    {"filename": "carrier_log_02.csv", "text": "Shipment_ID: SH-3301 | Tracking: TRK-1049 | Location: Atlanta, GA | Status: DELIVERED | Cost: $850.00 | Notes: Delivered on time to GA Hub."},
    {"filename": "carrier_log_03.csv", "text": "Shipment_ID: SH-8820 | Tracking: TRK-9902 | Location: Denver, CO | Status: EXCEPTION | Cost: $3,400.00 | Notes: Reefer unit failure reported in Denver hub."},
    {"filename": "carrier_log_04.csv", "text": "Shipment_ID: SH-5541 | Tracking: TRK-3381 | Location: Phoenix, AZ | Status: DELIVERED | Cost: $620.00 | Notes: Normal delivery in AZ territory."},
    {"filename": "carrier_log_05.csv", "text": "Shipment_ID: SH-9912 | Tracking: TRK-7711 | Location: Houston, TX | Status: DELAYED | Cost: $2,100.00 | Notes: Heavy congestion near Houston port terminal."}
]

if st.button("🚀 Seed Sample Data into LanceDB"):
    table = db.create_table("vendor_docs", data=sample_logs, mode="overwrite")
    st.success("✅ Sample database successfully created and indexed into `vendor_docs`!")

st.divider()

# --- 2. DYNAMIC CSV INGESTION PIPELINE ---
st.subheader("📤 Upload Custom Spreadsheet / CSV")
st.write("Upload custom telemetry CSV files. The engine automatically detects and combines all text columns into vector index strings.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        st.write("📋 **Preview of Uploaded Data:**", df_uploaded.head())

        # DYNAMIC COLUMN VECTORIZATION:
        # Automatically detect and combine all text/object columns into a single string column named 'text'
        if "text" not in df_uploaded.columns:
            text_cols = df_uploaded.select_dtypes(include=['object', 'string']).columns
            if len(text_cols) > 0:
                df_uploaded["text"] = df_uploaded[text_cols].astype(str).agg(" | ".join, axis=1)
                st.info(f"⚡ Automatically combined text columns `{list(text_cols)}` into dynamic search index.")
            else:
                # Fallback if no string columns were detected
                df_uploaded["text"] = df_uploaded.astype(str).agg(" | ".join, axis=1)

        # Add filename metadata if not present
        if "filename" not in df_uploaded.columns:
            df_uploaded["filename"] = uploaded_file.name

        if st.button("📥 Index Uploaded CSV into LanceDB"):
            if "vendor_docs" in db.table_names():
                table = db.open_table("vendor_docs")
                table.add(df_uploaded.to_dict(orient="records"))
            else:
                db.create_table("vendor_docs", data=df_uploaded.to_dict(orient="records"))
            st.success(f"✅ Successfully vectorized and indexed `{len(df_uploaded)}` rows into LanceDB!")

    except Exception as e:
        st.error(f"Error processing file: {e}")