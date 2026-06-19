import streamlit as st
import database as db
import os
import webbrowser

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

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ================= REPORT SYSTEM =================
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


# ================= FIREBASE SIGNUP =================
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


# ================= FIREBASE LOGIN =================
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


# ================= GOOGLE LOGIN UI (OPTIONAL BUTTON) =================
def google_login_ui():

    st.subheader("🔵 Sign in with Google")

    if st.button("Continue with Google"):

        # Firebase handles Google login in real setup
        st.info("Redirecting to Google login...")

        webbrowser.open("https://accounts.google.com")

        st.warning("Complete login in browser then return here.")


# ================= ROUTING =================
if not st.session_state.logged_in:

    st.title("🚀 Urban AI Login System")

    menu = st.radio("Choose Login Method", ["Login", "Sign Up", "Google Login"])

    if menu == "Login":
        firebase_login()

    elif menu == "Sign Up":
        firebase_signup()

    else:
        google_login_ui()

    st.stop()


# ================= AFTER LOGIN =================
import home
home.show_home()
