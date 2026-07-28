import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LATTICE_AI Control Tower",
    page_icon="🛡️",
    layout="wide",
)

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
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to view:", ["Home Dashboard", "Detailed Analytics", "System Settings"])

st.sidebar.divider()
if st.sidebar.button("Log Out"):
    st.session_state["password_correct"] = False
    st.rerun()

# -----------------------------------------------------------------------------
# 4. PAGE VIEW CONTROLLERS
# -----------------------------------------------------------------------------

# ==========================================
# PAGE 1: HOME DASHBOARD
# ==========================================
if page == "Home Dashboard":
    st.title("🛡️ Home - LATTICE_AI Control Tower")
    st.caption("Live System Telemetry & Vector DB Metrics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Neural Agents", "128", "+12 today")
    col2.metric("LanceDB Queries", "1.42M", "+8.5%")
    col3.metric("Avg Latency", "42 ms", "-4 ms")
    col4.metric("Uptime", "99.98%", "Nominal")

    st.divider()
    
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Real-Time Telemetry Throughput")
        chart_data = pd.DataFrame({
            "Timestamp": pd.date_range(start="2026-07-28 00:00", periods=24, freq="h"),
            "Vector Search Queries/sec": [120, 115, 90, 85, 95, 140, 310, 520, 780, 890, 950, 920, 880, 860, 890, 910, 840, 750, 620, 480, 350, 280, 190, 150],
            "Latency (ms)": [45, 44, 42, 41, 41, 43, 48, 55, 62, 65, 68, 64, 61, 60, 62, 63, 59, 54, 50, 48, 46, 45, 44, 43]
        })
        fig = px.line(chart_data, x="Timestamp", y=["Vector Search Queries/sec", "Latency (ms)"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("⚡ Cluster Health")
        health_data = pd.DataFrame({
            "Component": ["Vector Engine", "API Gateway", "Worker Nodes", "Cache Tier"],
            "Status": ["Healthy", "Healthy", "Warning", "Healthy"],
            "Load (%)": [68, 42, 89, 23]
        })
        st.dataframe(health_data, hide_index=True, use_container_width=True)

# ==========================================
# PAGE 2: DETAILED ANALYTICS
# ==========================================
elif page == "Detailed Analytics":
    st.title("📈 Detailed Analytics & Inspection")
    st.caption("Granular system performance and query latency breakdown.")

    # Time-range filter
    time_filter = st.selectbox("Select Time Horizon", ["Last 24 Hours", "Last 7 Days", "Last 30 Days"])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Query Latency Distribution (P95 vs P99)")
        latency_df = pd.DataFrame({
            "Percentile": ["P50 (Median)", "P90", "P95", "P99"],
            "Latency (ms)": [28, 45, 62, 115]
        })
        fig_bar = px.bar(latency_df, x="Percentile", y="Latency (ms)", color="Percentile", title="Response Latency Breakdown")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("🎯 Neural Agent Load Distribution")
        agent_df = pd.DataFrame({
            "Agent Group": ["Embedding Workers", "RAG Rerankers", "Safety Guardrails", "Telemetry Loggers"],
            "Allocation (%)": [40, 30, 20, 10]
        })
        fig_pie = px.pie(agent_df, names="Agent Group", values="Allocation (%)", title="Resource Allocation")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📜 Recent System Log Inspection")
    logs = pd.DataFrame({
        "Timestamp": ["2026-07-28 18:10:02", "2026-07-28 18:08:45", "2026-07-28 18:05:12", "2026-07-28 18:00:00"],
        "Severity": ["INFO", "WARNING", "INFO", "CRITICAL"],
        "Service": ["LanceDB", "Worker Node #4", "API Gateway", "Cache Tier"],
        "Message": ["Vector index compaction completed", "CPU utilization exceeded 85%", "Token authentication success", "Memcached connection timeout (resolved)"]
    })
    st.dataframe(logs, use_container_width=True)

# ==========================================
# PAGE 3: SYSTEM SETTINGS
# ==========================================
elif page == "System Settings":
    st.title("⚙️ System Configuration & Controls")
    st.caption("Manage cloud region deployments, telemetry verbosity, and system secrets.")

    with st.expander("🌐 Cloud Region Deployment", expanded=True):
        region = st.selectbox("Primary Cloud Region", ["US-East (N. Virginia)", "US-West (Oregon)", "EU-Central (Frankfurt)", "AP-South (Mumbai)"])
        st.multiselect("Active Failover Regions", ["US-East", "US-West", "EU-Central", "AP-South"], default=["US-East", "EU-Central"])

    with st.expander("🔊 Telemetry & Logging Controls", expanded=True):
        log_level = st.multiselect("Severity Levels to Capture", ["INFO", "WARNING", "ERROR", "CRITICAL"], default=["WARNING", "ERROR", "CRITICAL"])
        st.slider("Telemetry Sampling Rate (%)", min_value=1, max_value=100, value=100)

    with st.expander("🔒 Security & Secrets Status"):
        st.success("App Password protection is ACTIVE.")
        st.text_input("Secrets Storage Path", value=".streamlit/secrets.toml", disabled=True)

    if st.button("Save Settings"):
        st.success("Configuration updated successfully!")