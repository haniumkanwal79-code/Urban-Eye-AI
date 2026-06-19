import streamlit as st
import database as db
import os

# ================= REPORT SYSTEM =================
from pdf_utils import create_pdf
from email_utils import send_email

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

st.write("DB exists:", os.path.exists("issues.db"))

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ================= 🚨 REPORT SYSTEM =================
def generate_report(issue_type, location, image_path):

    try:
        pdf_path = create_pdf(issue_type, location, image_path)

        subject = f"🚨 Urban Issue Detected: {issue_type}"

        body = f"""
🚨 New Urban Issue Detected

Issue Type: {issue_type}
Location: {location}

Please check attached PDF report.
        """

        send_email(subject, body, pdf_path)

        st.success("📧 Report generated & email sent successfully!")

    except Exception as e:
        st.error(f"Report Error: {e}")


# ================= 🔐 FIREBASE LOGIN =================
def firebase_login():

    st.title("🔐 Urban AI Login (Firebase)")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login with Firebase"):

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

    firebase_login()
    st.stop()


# ================= AFTER LOGIN =================
import home
home.show_home()
