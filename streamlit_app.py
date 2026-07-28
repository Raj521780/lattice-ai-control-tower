import streamlit as st

st.set_page_config(
    page_title="LATTICE_AI — Control Tower",
    page_icon="⚡",
    layout="wide"
)

# Multi-Page Setup
pages = {
    "Operational Hub": [
        st.Page("views/1_telemetry.py", title="Executive Telemetry Search", icon="🔍"),
        st.Page("views/2_analytics.py", title="Fleet Telemetry Analytics", icon="📊"),
        st.Page("views/4_alerts_api.py", title="Alerts & ERP Integration", icon="🚨"),
    ],
    "Data & Management": [
        st.Page("views/3_ingestion.py", title="Data Hub & Ingestion Engine", icon="📁"),
    ]
}

pg = st.navigation(pages)
pg.run()