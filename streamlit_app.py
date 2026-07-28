import streamlit as st
import pandas as pd
import plotly.express as px
from auth import require_password

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & AUTH
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LATTICE_AI Control Tower",
    page_icon="🛡️",
    layout="wide",
)

# Enforce password gate BEFORE anything else renders
require_password()

# -----------------------------------------------------------------------------
# 2. HOME PAGE DASHBOARD
# -----------------------------------------------------------------------------
st.title("🛡️ Home - LATTICE_AI Control Tower")
st.caption("Live System Telemetry & Vector DB Metrics")

# Sidebar Log Out Button
with st.sidebar:
    if st.button("Log Out"):
        st.session_state["password_correct"] = False
        st.rerun()

# --- METRIC CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Active Neural Agents", value="128", delta="+12 today")
col2.metric(label="LanceDB Vector Queries", value="1.42M", delta="+8.5%")
col3.metric(label="Avg Response Latency", value="42 ms", delta="-4 ms")
col4.metric(label="System Uptime", value="99.98%", delta="Nominal")

st.divider()

# --- CHART ---
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