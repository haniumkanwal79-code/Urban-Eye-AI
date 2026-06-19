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


# ================= PREMIUM UI STYLE =================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: radial-gradient(circle at top, #0b1220, #050814);
    color: white;
}

/* TITLE */
.main-title {
    font-size:42px;
    font-weight:900;
    text-align:center;
    color:#00e5ff;
    text-shadow:0px 0px 20px rgba(0,229,255,0.6);
    margin-top:20px;
}

.sub-title {
    text-align:center;
    color:#a9c4d8;
    font-size:16px;
    margin-bottom:30px;
}

/* LOGIN CARD */
.login-box {
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(12px);
    padding:30px;
    border-radius:18px;
    box-shadow:0px 0px 25px rgba(0,229,255,0.15);
    max-width:420px;
    margin:auto;
    border:1px solid rgba(0,229,255,0.25);
}

/* INPUTS */
input {
    border-radius:10px !important;
}

/* BUTTON */
.stButton button {
    width:100%;
    background: linear-gradient(90deg, #00e5ff, #00ffcc);
    color:black;
    font-weight:bold;
    border-radius:10px;
    border:none;
    padding:10px;
}

.stButton button:hover {
    transform: scale(1.03);
    box-shadow:0px 0px 15px rgba(0,255,204,0.5);
}

/* RADIO */
.stRadio > div {
    background: rgba(255,255,255,0.05);
    padding:10px;
    border-radius:10px;
}

/* FOOTER TEXT */
.footer {
    text-align:center;
    color:gray;
    font-size:12px;
    margin-top:20px;
}

</style>
""", unsafe_allow_html=True)


# ================= REPORT SYSTEM (PDF ONLY) =================
def generate_report(issue_type, location, image_path):

    try:
        pdf_path = create_pdf(issue_type, location, image_path)

        st.success("📄 PDF Report Generated Successfully!")

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇ Download Report PDF",
                data=f,
                file_name="urban_issue_report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Report Error: {e}")


# ================= SIGNUP =================
def firebase_signup():

    st.markdown("### 🆕 Create Account")

    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    if st.button("Create Account 🚀"):
        try:
            auth.create_user_with_email_and_password(email, password)
            st.success("Account Created Successfully 🚀 Now Login")

        except Exception as e:
            st.error(f"Signup Failed ❌ {e}")


# ================= LOGIN =================
def firebase_login():

    st.markdown("### 🔐 Secure Login Portal")

    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    if st.button("Login 🚀"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)

            st.session_state.logged_in = True
            st.session_state.user = email

            st.success("Login Successful 🚀 Redirecting...")
            st.rerun()

        except Exception as e:
            st.error(f"Login Failed ❌ {e}")


# ================= ROUTING =================
if not st.session_state.logged_in:

    st.markdown("<div class='main-title'>🏛 Urban AI Intelligence System</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Secure Government Surveillance Platform</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    menu = st.radio("Select Action", ["Login", "Sign Up"])

    if menu == "Login":
        firebase_login()
    else:
        firebase_signup()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer'>🔐 Powered by Firebase Authentication | Secure Access System</div>", unsafe_allow_html=True)

    st.stop()


# ================= AFTER LOGIN =================
import home
home.show_home()
