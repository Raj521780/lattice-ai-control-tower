import streamlit as st
from auth import require_password

# Keep password gate intact on sub-pages
require_password()

st.title("📈 Detailed Analytics")
st.write("This sub-page is protected by the same login session! You won't be asked for a password again when navigating here.")