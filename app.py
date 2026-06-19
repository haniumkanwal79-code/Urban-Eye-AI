import streamlit as st
import database as db
import os

# ================= REPORT SYSTEM =================
from pdf_utils import create_pdf
from email_utils import send_email

# ================= FIREBASE AUTH =================
import pyrebase

firebaseConfig = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_AUTH_DOMAIN",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_STORAGE_BUCKET",
    "messagingSenderId": "YOUR_MESSAGING_ID",
    "appId": "YOUR_APP_ID"
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

    pdf_path = create_pdf(issue_type, location, image_path)

    subject = f"🚨 Urban Issue Detected: {issue_type}"

    body = f"""
    New Urban Issue Detected 🚨

    Issue Type: {issue_type}
    Location: {location}

    Please check attached PDF report.
    """

    send_email(subject, body, pdf_path)


# ================= 🔐 FIREBASE LOGIN =================
def firebase_login():

    st.title("🔐 Urban AI Login (Firebase)")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login with Google/Firebase"):

        try:
            user = auth.sign_in_with_email_and_password(email, password)

            st.session_state.logged_in = True
            st.session_state.user = email

            st.success("Login Successful 🚀")
            st.rerun()

        except Exception as e:
            st.error("Login Failed ❌ Check credentials")


# ================= ROUTING =================
if not st.session_state.logged_in:

    firebase_login()
    st.stop()


# ================= AFTER LOGIN =================
import home
home.show_home()
