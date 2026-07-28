import streamlit as st
import pandas as pd
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
# 2. PASSWORD PROTECTION
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
# 3. SIDEBAR NAVIGATION (SINGLE-FILE MULTI-PAGE)
# -----------------------------------------------------------------------------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to page:", ["Home Dashboard", "Detailed Analytics", "System Settings"])

st.sidebar.divider()
if st.sidebar.button("Log Out"):
    st.session_state["password_correct"] = False
    st.rerun()

# -----------------------------------------------------------------------------
# 4. PAGE CONTROLLERS
# -----------------------------------------------------------------------------

# --- PAGE 1: HOME DASHBOARD ---
if page == "Home Dashboard":
    st.title("🛡️ Home - LATTICE_AI Control Tower")
    st.caption("Live System Telemetry & Vector DB Metrics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Neural Agents", "128", "+12 today")
    col2.metric("LanceDB Queries", "1.42M", "+8.5%")
    col3.metric("Avg Latency", "42 ms", "-4 ms")
    col4.metric("Uptime", "99.98%", "Nominal")

    st.divider()
    st.subheader("📈 Real-Time Telemetry Throughput")
    
    chart_data = pd.DataFrame({
        "Timestamp": pd.date_range(start="2026-07-28 00:00", periods=24, freq="h"),
        "Vector Search Queries/sec": [120, 115, 90, 85, 95, 140, 310, 520, 780, 890, 950, 920, 880, 860, 890, 910, 840, 750, 620, 480, 350, 280, 190, 150],
        "Latency (ms)": [45, 44, 42, 41, 41, 43, 48, 55, 62, 65, 68, 64, 61, 60, 62, 63, 59, 54, 50, 48, 46, 45, 44, 43]
    })
    
    fig = px.line(chart_data, x="Timestamp", y=["Vector Search Queries/sec", "Latency (ms)"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE 2: ANALYTICS ---
elif page == "Detailed Analytics":
    st.title("📈 Detailed Analytics")
    st.write("Welcome to the granular system inspection view.")
    st.info("Because navigation is built into state, switching back and forth does NOT ask for password again!")

# --- PAGE 3: SETTINGS ---
elif page == "System Settings":
    st.title("⚙️ System Settings")
    st.selectbox("Select Cloud Region", ["US-East", "US-West", "EU-Central", "AP-South"])
    st.multiselect("Telemetry Severity", ["INFO", "WARNING", "ERROR", "CRITICAL"], default=["ERROR", "CRITICAL"])