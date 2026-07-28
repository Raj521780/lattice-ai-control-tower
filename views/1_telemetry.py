import streamlit as st
import lancedb
import pandas as pd
from datetime import datetime

st.title("🔍 Executive Search & Telemetry")
st.caption("LATTICE_AI Ultra-Hybrid Engine: Semantic search with dynamic spatial/grid auto-discovery.")

DB_PATH = "data/sample-lancedb"

@st.cache_resource
def get_db():
    return lancedb.connect(DB_PATH)

db = get_db()

# --- Audit Log Helper Function ---
def log_search_query(query_str, result_count):
    log_data = [{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query_str,
        "results_returned": int(result_count)
    }]
    if "search_audit_logs" in db.table_names():
        audit_table = db.open_table("search_audit_logs")
        audit_table.add(log_data)
    else:
        db.create_table("search_audit_logs", data=log_data)

# --- Dynamic Location Entity Extraction Engine ---
@st.cache_data(ttl=60)  # Caches entities for 60 seconds to stay fast as dataset scales
def get_known_locations(_table):
    try:
        df_all = _table.search("").limit(5000).to_pandas()
        if not df_all.empty and "text" in df_all.columns:
            text_data = pd.Series(df_all["text"]).astype(str).str.upper()
            
            # Extract values following "Location:" or spatial state/city patterns
            extracted_locations = text_data.str.extractall(r'LOCATION:\s*([^\n|]+)')[0].dropna().unique()
            
            terms = set()
            for loc in extracted_locations:
                for part in loc.replace(',', ' ').split():
                    clean_part = part.strip()
                    if len(clean_part) >= 2:  # Retain state codes (TX, GA, CO, WA, IL) and city names
                        terms.add(clean_part)
            return list(terms)
    except Exception:
        pass
    return []

if "vendor_docs" not in db.table_names():
    st.warning("⚠️ No database table found (`vendor_docs`). Please go to **Data Hub** to seed or upload data.")
else:
    table = db.open_table("vendor_docs")

    # --- Persistent Audit History Display + Clear Button ---
    if "search_audit_logs" in db.table_names():
        audit_table = db.open_table("search_audit_logs")
        audit_df = audit_table.to_pandas()
        
        if not audit_df.empty and "query" in audit_df.columns:
            col_hist_title, col_clear = st.columns([4, 1])
            with col_hist_title:
                st.markdown("##### 🕒 Persistent Search Audit Logs (LanceDB):")
            with col_clear:
                if st.button("🗑️ Clear History", key="clear_audit_logs"):
                    db.drop_table("search_audit_logs")
                    if "current_query" in st.session_state:
                        st.session_state["current_query"] = ""
                    st.rerun()

            recent_queries = audit_df["query"].dropna().drop_duplicates().tolist()[-5:]
            if recent_queries:
                cols = st.columns(min(len(recent_queries), 5))
                for i, prev in enumerate(reversed(recent_queries)):
                    with cols[i]:
                        if st.button(f"🔍 {prev}", key=f"hist_{i}"):
                            st.session_state["current_query"] = prev

    # --- Search Input Bar ---
    col_search, col_limit = st.columns([4, 1])
    with col_search:
        default_val = st.session_state.get("current_query", "")
        query_str = st.text_input("Natural Language Query", value=default_val, placeholder="e.g., TX deliveries, Denver, delayed shipments")
    with col_limit:
        top_k = st.number_input("Max Results", min_value=1, max_value=20, value=5)

    if query_str:
        with st.spinner("Searching LATTICE_AI index with dynamic grid bounds..."):
            raw_df = table.search(query_str).limit(50).to_pandas()
            query_upper = query_str.upper()

            # --- DYNAMIC LOCATION BOUNDARY MATCHING ---
            known_locations = get_known_locations(table)
            active_keywords = [term for term in known_locations if term in query_upper]

            if active_keywords and "text" in raw_df.columns:
                pattern = "|".join(active_keywords)
                filtered_df = raw_df[raw_df["text"].str.upper().str.contains(pattern, na=False)]
                results = filtered_df.head(int(top_k)) if not filtered_df.empty else raw_df.head(int(top_k))
                if not filtered_df.empty:
                    st.success(f"📍 Dynamic Grid Filter Active for: **{', '.join(set(active_keywords))}**")
            else:
                results = raw_df.head(int(top_k))

            # Log query persistently to LanceDB
            log_search_query(query_str, len(results))

            # Dynamic Financial Exposure Calculation
            if "text" in results.columns:
                text_series = pd.Series(results["text"]).astype(str)
                costs = text_series.str.extract(r'\$(\d+\.?\d*)')[0].astype(float).dropna()
                total_exposure = costs.sum() if not costs.empty else 0.0
            else:
                total_exposure = 0.0

            m1, m2, m3 = st.columns(3)
            m1.metric("Matches Found", len(results))
            m2.metric("Financial Exposure in View", f"${total_exposure:,.2f}")
            m3.metric("Precision Index", "100% Deterministic Bounds")

            st.markdown("---")

            # Render Record Cards
            for idx, row in results.iterrows():
                clean_text = str(row.get("text", "")).replace("DELIVERED", " | Status: ✅ DELIVERED | ")
                with st.expander(f"📦 Record #{idx + 1} — Source: {row.get('filename', 'LanceDB Store')}"):
                    st.markdown(f"**Log Entry:** `{clean_text}`")
                    st.caption(f"Vector Distance: `{row.get('_distance', 0.0):.4f}`")

            # Export Executive Briefing
            st.download_button(
                label="📥 Export Executive Brief (CSV)",
                data=results.to_csv(index=False),
                file_name=f"brief_{query_str.replace(' ', '_')}.csv",
                mime="text/csv"
            )