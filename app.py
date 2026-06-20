import streamlit as st
import database as db
import os

# ================= REPORT SYSTEM (ONLY PDF) =================
from pdf_utils import create_pdf

# ================= FIREBASE AUTH =================
import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyBg4jTdlcrqKwNa0115fJN6rQsUtorZp58",
    "authDomain": "urban-ai-145b8.firebaseapp.com",
    "projectId": "urban-ai-145b8",
    "storageBucket": "urban-ai-145b8.appspot.com",
    "messagingSenderId": "747825183051",
    "appId": "1:747825183051:web:6cb5fc015813525808d0ce",
    "databaseURL": "https://urban-ai-145b8.firebaseio.com"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# ================= DATABASE INIT =================
db.create_table()

os.makedirs("reports", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ================= 🚨 REPORT SYSTEM (PDF ONLY) =================
def generate_report(issue_type, location, image_path):

    try:
        pdf_path = create_pdf(issue_type, location, image_path)

        st.success("📄 PDF Report Generated Successfully!")

        # show download button
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇ Download Report PDF",
                data=f,
                file_name="urban_issue_report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Report Error: {e}")


# ================= 🔐 SIGNUP =================
def firebase_signup():

    st.subheader("🆕 Create New Account")

    email = st.text_input("Signup Email")
    password = st.text_input("Signup Password", type="password")

    if st.button("Create Account"):

        try:
            auth.create_user_with_email_and_password(email, password)
            st.success("Account Created Successfully 🚀 Now Login")

        except Exception as e:
            st.error(f"Signup Failed ❌ {e}")


# ================= 🔐 LOGIN =================
def firebase_login():

    st.subheader("🔐 Login")

    email = st.text_input("Login Email")
    password = st.text_input("Login Password", type="password")

    if st.button("Login"):

        try:
            user = auth.sign_in_with_email_and_password(email, password)

            st.session_state.logged_in = True
            st.session_state.user = email

            st.success("Login Successful 🚀")
            st.rerun()

        except Exception as e:
            st.error(f"Login Failed ❌ {e}")


# ================= ROUTING =================
if not st.session_state.logged_in:

    menu = st.radio("Choose Action", ["Login", "Sign Up"])

    if menu == "Login":
        firebase_login()

    else:
        firebase_signup()

    st.stop()


# ================= AFTER LOGIN =================
import home
home.show_home()
