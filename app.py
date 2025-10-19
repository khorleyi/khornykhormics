import streamlit as st

st.set_page_config(
    page_title="Story Creator",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'api_response' not in st.session_state:
    st.session_state.api_response = None

if 'current_panel' not in st.session_state:
    st.session_state.current_panel = 1

# Main page content
st.title("📖 Story Creator")
st.write("Welcome to Story Creator! Use the sidebar to input your story and characters.")

# This is the homepage - redirect to input page
st.info("👈 Please use the sidebar to navigate to the Input page to get started.")
