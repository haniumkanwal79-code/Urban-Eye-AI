import streamlit as st

def show_home():
    st.title("🏠 Dashboard")

    st.write("Welcome to Home Page 🚀")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
