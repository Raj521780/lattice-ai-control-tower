import streamlit as st

def require_password():
    """Forces password check on any page where it is called."""
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
                st.error("❌ Incorrect password. Please try again.")

    st.stop()