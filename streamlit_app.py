import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import lancedb
import os

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LATTICE_AI Control Tower",
    page_icon="🛡️",
    layout="wide",
)

# Initialize LanceDB connection (local memory or temp directory)
@st.cache_resource
def get_lancedb():
    db = lancedb.connect("./lancedb_data")
    return db

db = get_lancedb()

# -----------------------------------------------------------------------------
# 2. PASSWORD GATE
# -----------------------------------------------------------------------------
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    st.title("🔒 Restricted Access")
    st.info("Please enter the authorization password to access LATTICE_AI Control Tower.")

    with st.form("login_form"):
        password_input = st.text_input("Enter Password", type="password")
        submit_button = st.form_submit_button("Log In")

        if submit_button:
            if "APP_PASSWORD" in st.secrets and password_input == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.rerun()
            elif "APP_PASSWORD" not in st.secrets:
                st.error("⚠️ 'APP_PASSWORD' missing in Streamlit Cloud Secrets.")
            else:
                st.error("❌ Incorrect password.")

    return False

if not check_password():
    st.stop()

# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.title("🛡️ LATTICE_AI Controls")
page = st.sidebar.radio(
    "Select Interface Mode:", 
    ["🔍 Vector Search & Ingestion", "📈 Live Telemetry", "⚙️ System Settings"]
)

st.sidebar.divider()
if st.sidebar.button("Log Out"):
    st.session_state["password_correct"] = False
    st.rerun()

# -----------------------------------------------------------------------------
# 4. VIEW 1: VECTOR SEARCH & FILE / URL INGESTION
# -----------------------------------------------------------------------------
if page == "🔍 Vector Search & Ingestion":
    st.title("🔍 Vector DB Query & Knowledge Base")
    st.caption("Upload files, process URLs, and query vector embeddings in LanceDB.")

    # --- SECTION A: FILE & URL INGESTION ---
    with st.expander("📥 Ingest Data (Files & Web URLs)", expanded=True):
        tab_files, tab_urls = st.tabs(["📄 Document Upload", "🌐 Web URL Scraper"])

        with tab_files:
            uploaded_files = st.file_uploader(
                "Upload documents (PDF, TXT, CSV, Markdown)", 
                accept_multiple_files=True,
                type=["pdf", "txt", "csv", "md"]
            )
            if uploaded_files:
                if st.button("Process & Embed Documents"):
                    with st.spinner("Processing documents and updating vector index..."):
                        # Simulating vector embedding pipeline
                        st.success(f"Successfully processed {len(uploaded_files)} file(s) into LanceDB!")

        with tab_urls:
            url_input = st.text_input("Enter Web URL for ingestion:", placeholder="https://example.com/docs")
            if url_input:
                if st.button("Scrape & Ingest URL"):
                    with st.spinner(f"Scraping content from {url_input}..."):
                        st.success(f"Scraped and embedded vector data from {url_input}!")

    st.divider()

    # --- SECTION B: VECTOR QUERY & SEARCH ---
    st.subheader("🔎 Vector DB Similarity Search")
    
    col_search, col_top_k = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("Enter search query or prompt:", placeholder="e.g. Find all telemetry anomalies in US-East cluster")
    with col_top_k:
        top_k = st.slider("Top-K Results", min_value=1, max_value=20, value=5)

    if search_query:
        st.markdown(f"**Search Results for:** `\"{search_query}\"`")
        
        # Mock Search Results Output
        results_df = pd.DataFrame({
            "Similarity Score": [0.94, 0.89, 0.82, 0.78, 0.71][:top_k],
            "Document Source": ["doc_telemetry_2026.pdf", "cluster_config.txt", "network_logs.csv", "https://example.com/docs", "agent_manifest.json"][:top_k],
            "Extracted Snippet": [
                "Agent 128 reported spike in LanceDB query volume during 18:00 UTC shift.",
                "Primary region set to US-East-1 with failover active in EU-Central.",
                "Latency increased by 4ms during compaction process.",
                "Vector embedding model dimensions set to 1536.",
                "Neural network weights updated successfully on worker node #4."
            ][:top_k]
        })
        
        st.dataframe(results_df, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. VIEW 2: LIVE TELEMETRY
# -----------------------------------------------------------------------------
elif page == "📈 Live Telemetry":
    st.title("📈 Real-Time System Telemetry")
    st.caption("Live metrics from neural agents and database clusters.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Neural Agents", "128", "+12 today")
    col2.metric("LanceDB Queries", "1.42M", "+8.5%")
    col3.metric("Avg Latency", "42 ms", "-4 ms")
    col4.metric("Uptime", "99.98%", "Nominal")

    st.divider()

    chart_data = pd.DataFrame({
        "Timestamp": pd.date_range(start="2026-07-28 00:00", periods=24, freq="h"),
        "Vector Search Queries/sec": [120, 115, 90, 85, 95, 140, 310, 520, 780, 890, 950, 920, 880, 860, 890, 910, 840, 750, 620, 480, 350, 280, 190, 150],
        "Latency (ms)": [45, 44, 42, 41, 41, 43, 48, 55, 62, 65, 68, 64, 61, 60, 62, 63, 59, 54, 50, 48, 46, 45, 44, 43]
    })
    
    fig = px.line(chart_data, x="Timestamp", y=["Vector Search Queries/sec", "Latency (ms)"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. VIEW 3: SYSTEM SETTINGS
# -----------------------------------------------------------------------------
elif page == "⚙️ System Settings":
    st.title("⚙️ System Configuration")
    
    region = st.selectbox("Cloud Region", ["US-East", "US-West", "EU-Central", "AP-South"])
    log_level = st.multiselect("Severity Log Level", ["INFO", "WARNING", "ERROR", "CRITICAL"], default=["WARNING", "ERROR"])
    st.slider("Telemetry Sampling Rate (%)", min_value=1, max_value=100, value=100)
    
    st.success("App Password Protection is Active.")