import streamlit as st
import pandas as pd
import plotly.express as px
import lancedb

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LATTICE_AI Control Tower",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. PASSWORD PROTECTION GATE
# -----------------------------------------------------------------------------
def check_password():
    """Returns True if the user enters the correct password stored in st.secrets."""
    if st.session_state.get("password_correct", False):
        return True

    st.title("🔒 Restricted Access")
    st.markdown("### Welcome to **LATTICE_AI Enterprise Control Tower**")
    st.info("Please enter the authorization password to access the telemetry dashboard.")

    # Create password input form
    with st.form("login_form"):
        password_input = st.text_input("Enter Password", type="password")
        submit_button = st.form_submit_button("Log In")

    if submit_button:
        # Check password against Streamlit Secrets
        if "APP_PASSWORD" in st.secrets and password_input == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            st.rerun()
        elif "APP_PASSWORD" not in st.secrets:
            # Fallback if secrets aren't set up yet on local machine
            st.warning("⚠️ 'APP_PASSWORD' not found in Secrets. Please add it in Streamlit Cloud settings.")
        else:
            st.error("❌ Incorrect password. Please try again.")

    return False

# Stop execution here if password is not verified
if not check_password():
    st.stop()

# -----------------------------------------------------------------------------
# 3. MAIN CONTROL TOWER APPLICATION (Executes after password is standard)
# -----------------------------------------------------------------------------

st.title("🛡️ LATTICE_AI Enterprise Control Tower")
st.caption("Live System Telemetry & Vector DB Vector Search Metrics")

# --- SIDEBAR CONTROLS ---
st.sidebar.title("Settings & Filters")
if st.sidebar.button("Log Out"):
    st.session_state["password_correct"] = False
    st.rerun()

st.sidebar.divider()
st.sidebar.header("System Controls")
region = st.sidebar.selectbox("Select Cloud Region", ["All Regions", "US-East", "US-West", "EU-Central", "AP-South"])
log_level = st.sidebar.multiselect("Telemetry Severity", ["INFO", "WARNING", "ERROR", "CRITICAL"], default=["INFO", "WARNING", "ERROR"])

# --- METRIC CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Active Neural Agents", value="128", delta="+12 today")
col2.metric(label="LanceDB Vector Queries", value="1.42M", delta="+8.5%")
col3.metric(label="Avg Response Latency", value="42 ms", delta="-4 ms")
col4.metric(label="System Uptime", value="99.98%", delta="Nominal")

st.divider()

# --- ANALYTICS & VISUALIZATIONS ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Real-Time Telemetry Throughput")
    
    # Sample time series data
    chart_data = pd.DataFrame({
        "Timestamp": pd.date_range(start="2026-07-28 00:00", periods=24, freq="h"),
        "Vector Search Queries/sec": [120, 115, 90, 85, 95, 140, 310, 520, 780, 890, 950, 920, 880, 860, 890, 910, 840, 750, 620, 480, 350, 280, 190, 150],
        "Latency (ms)": [45, 44, 42, 41, 41, 43, 48, 55, 62, 65, 68, 64, 61, 60, 62, 63, 59, 54, 50, 48, 46, 45, 44, 43]
    })
    
    fig = px.line(
        chart_data, 
        x="Timestamp", 
        y=["Vector Search Queries/sec", "Latency (ms)"],
        title="Query Volume vs. Response Latency (24h)",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("⚡ Cluster Health")
    health_data = pd.DataFrame({
        "Component": ["Vector Engine", "API Gateway", "Worker Nodes", "Cache Tier"],
        "Status": ["Healthy", "Healthy", "Warning", "Healthy"],
        "Load (%)": [68, 42, 89, 23]
    })
    st.dataframe(health_data, hide_index=True, use_container_width=True)

    st.subheader("🔒 Active Secrets")
    st.success("App Password protection is active.")