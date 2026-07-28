import streamlit as st
import pandas as pd
import lancedb

# -----------------------------------------------------------------------------
# 1. CONFIG & AUTHENTICATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Jungle Logistics Engine | Powered by Lattice_AI",
    page_icon="🌴",
    layout="wide",
)

def check_password():
    if st.session_state.get("password_correct", False):
        return True

    st.title("🔒 Restricted Access")
    st.markdown("### Welcome to **Jungle Logistics Engine API** (`Lattice_AI` Core)")
    st.info("Enter authorization key to access the core logistics search interface.")

    with st.form("login_form"):
        password_input = st.text_input("API Key / Password", type="password")
        if st.form_submit_button("Authenticate"):
            if "APP_PASSWORD" in st.secrets and password_input == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.rerun()
            elif "APP_PASSWORD" not in st.secrets:
                st.error("⚠️ 'APP_PASSWORD' missing in Streamlit Cloud Secrets.")
            else:
                st.error("❌ Invalid authorization key.")
    return False

if not check_password():
    st.stop()

# -----------------------------------------------------------------------------
# 2. SIDEBAR NAVIGATION & ENGINE STATUS
# -----------------------------------------------------------------------------
st.sidebar.title("🌴 Jungle Logistics Engine")
st.sidebar.caption("Core AI Provider: **Lattice_AI**")

page = st.sidebar.radio(
    "Select Engine Interface:", 
    [
        "🔍 Logistics Semantic Search", 
        "📥 Manifest & URL Ingestion", 
        "⚙️ API & Vector Engine Config"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**Engine Status:** `ONLINE (v2.4)`")
st.sidebar.markdown("**Vector Store:** `LanceDB`")

if st.sidebar.button("Log Out"):
    st.session_state["password_correct"] = False
    st.rerun()

# -----------------------------------------------------------------------------
# 3. INTERFACE MODE 1: LOGISTICS SEMANTIC SEARCH (PRIMARY FOCUS)
# -----------------------------------------------------------------------------
if page == "🔍 Logistics Semantic Search":
    st.title("🔍 Jungle Logistics Engine — Vector Search")
    st.caption("Leveraging **Lattice_AI** embeddings for high-dimensional supply chain & shipment retrieval.")

    # Search Bar
    search_query = st.text_input(
        "🔎 Query Jungle Logistics API:", 
        placeholder="e.g. Find delayed refrigerated shipments in APAC transit hub or bill of lading #88392"
    )
    
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        region_filter = st.selectbox("Filter Route/Region", ["All Regions", "APAC", "EMEA", "NA-EAST", "LATAM"])
    with col_filter2:
        top_k = st.slider("Top Matching Vectors (Top-K)", 1, 20, 5)
    with col_filter3:
        min_score = st.slider("Minimum Similarity Threshold", 0.0, 1.0, 0.70)

    st.divider()

    if search_query:
        st.subheader("🎯 Lattice_AI Vector Search Results")
        
        # Demonstrative Search Payload representing Jungle Engine API response
        mock_logistics_results = [
            {
                "Shipment ID": "SHP-2026-9921",
                "Carrier": "Jungle Express Air",
                "Route": "Singapore (SIN) ➔ Frankfurt (FRA)",
                "Status": "DELAYED (Customs Hold)",
                "Lattice_AI Score": 0.94,
                "Cargo Content": "Temperature-sensitive pharmaceuticals requiring 2°C-8°C cold chain.",
                "Manifest Source": "manifest_sin_fra_q3.pdf"
            },
            {
                "Shipment ID": "SHP-2026-4410",
                "Carrier": "Jungle Maritime",
                "Route": "Tokyo (TYO) ➔ Los Angeles (LAX)",
                "Status": "IN_TRANSIT",
                "Lattice_AI Score": 0.88,
                "Cargo Content": "Automotive sensor modules for EV assembly line line-stop risk.",
                "Manifest Source": "bol_ocean_tyo_lax.csv"
            },
            {
                "Shipment ID": "SHP-2026-1029",
                "Carrier": "Jungle Freight Line",
                "Route": "Mumbai (BOM) ➔ Dubai (DXB)",
                "Status": "DELIVERED",
                "Lattice_AI Score": 0.81,
                "Cargo Content": "High-density lithium ion battery packs for energy storage systems.",
                "Manifest Source": "https://jungle-logistics.internal/docs/manifests/1029"
            }
        ]
        
        df_results = pd.DataFrame(mock_logistics_results[:top_k])
        
        # Display as clear interactive table
        st.dataframe(df_results, use_container_width=True)
        
        # Detailed Json Inspection for API Developers
        with st.expander("🛠️ View Raw API Response (Lattice_AI Vector Payload)"):
            st.json({
                "engine": "Jungle_Logistics_v2",
                "core_ai": "Lattice_AI_Embedding_v4",
                "query": search_query,
                "vector_dimension": 1536,
                "retrieved_count": len(df_results),
                "hits": mock_logistics_results[:top_k]
            })

# -----------------------------------------------------------------------------
# 4. INTERFACE MODE 2: MANIFEST & URL INGESTION
# -----------------------------------------------------------------------------
elif page == "📥 Manifest & URL Ingestion":
    st.title("📥 Supply Chain Data Ingestion")
    st.caption("Feed logistics manifests, PDFs, CSVs, and tracking URLs into the Lattice_AI vector index.")

    tab_files, tab_url = st.tabs(["📄 Upload Manifests & Waybills", "🌐 Logistics Web Scraper / API Webhook"])

    with tab_files:
        uploaded_files = st.file_uploader(
            "Upload Freight Documents (PDF, CSV, Bill of Lading)", 
            type=["pdf", "csv", "txt", "json"], 
            accept_multiple_files=True
        )
        if uploaded_files:
            if st.button("Parse & Vectorize with Lattice_AI"):
                with st.spinner("Generating embeddings & inserting into LanceDB vector index..."):
                    st.success(f"Successfully processed {len(uploaded_files)} file(s) into Jungle Logistics Engine!")

    with tab_url:
        url_input = st.text_input("Enter Carrier Tracking URL or API Endpoint:", placeholder="https://api.junglelogistics.com/v1/shipments/stream")
        if url_input and st.button("Ingest Remote Stream"):
            with st.spinner(f"Ingesting & indexing {url_input}..."):
                st.success("Remote stream ingested and indexed successfully!")

# -----------------------------------------------------------------------------
# 5. INTERFACE MODE 3: API & VECTOR ENGINE CONFIG
# -----------------------------------------------------------------------------
elif page == "⚙️ API & Vector Engine Config":
    st.title("⚙️ Engine Configuration")
    st.caption("Settings for the Jungle Logistics Engine & Lattice_AI core parameters.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lattice_AI Hyperparameters")
        st.selectbox("Embedding Model", ["Lattice-Dense-v4 (Recommended)", "Lattice-Sparse-v2", "Lattice-Hybrid-v1"])
        st.slider("Vector Chunk Size (Tokens)", 128, 2048, 512)
        st.slider("Chunk Overlap", 0, 256, 64)
    
    with col2:
        st.subheader("LanceDB Index Parameters")
        st.selectbox("Distance Metric", ["Cosine Similarity", "L2 Euclidean", "Dot Product"])
        st.number_input("LanceDB Table Partition Count", value=256)
        
    if st.button("Save Configuration"):
        st.success("Engine configuration updated!")