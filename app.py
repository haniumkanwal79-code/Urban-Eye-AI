import streamlit as st
import database as db
import os

# ================= REPORT SYSTEM (ONLY PDF) =================
from pdf_utils import create_pdf

# ================= FIREBASE AUTH =================
import pyrebase
# Google ID token verify karne ke liye secondary processing libraries
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

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

# ================= SESSION (FIXED FOR STABILITY) =================
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

/* GOOGLE BUTTON SEPARATOR */
.or-separator {
    text-align: center;
    margin: 15px 0;
    color: #a9c4d8;
    font-size: 14px;
    position: relative;
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

    email = st.text_input("Email Address", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_pass")

    if st.button("Create Account 🚀"):
        try:
            auth.create_user_with_email_and_password(email, password)
            st.success("Account Created Successfully 🚀 Now Login")

        except Exception as e:
            st.error(f"Signup Failed ❌ {e}")


# ================= GOOGLE AUTH SYSTEM (OPTIMIZED) =================
def google_login_component():
    """
    Handles Google Authentication for Firebase using secure redirection keys.
    Fixes state management so user doesn't get logged out repeatedly.
    """
    try:
        client_id = st.secrets["google_oauth"]["CLIENT_ID"]
        client_secret = st.secrets["google_oauth"]["CLIENT_SECRET"]
        redirect_uri = st.secrets["google_oauth"]["REDIRECT_URI"]
    except Exception:
        st.warning("⚠️ Google Sign-In setup pending in Streamlit secrets.toml")
        return

    st.markdown('<div class="or-separator">─ OR ─</div>', unsafe_allow_html=True)

    # Google Client Configuration payload
    from google_auth_oauthlib.flow import Flow
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri=redirect_uri
    )

    auth_url, _ = flow.authorization_url(prompt='select_account')

    # Render a fully styled premium standard Google Sign-In button
    st.markdown(f'''
        <a href="{auth_url}" target="_self" style="text-decoration: none;">
            <button style="background-color: #ffffff; color: #2d3748; font-weight: bold; border: 1px solid #dadce0; padding: 10px 15px; border-radius: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 100%; transition: 0.2s;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" style="width: 18px; margin-right: 12px;"/>
                Continue with Google
            </button>
        </a>
    ''', unsafe_allow_html=True)

    # Catch OAuth authentication callback codes from URLs safely
    query_params = st.query_params
    if "code" in query_params:
        try:
            flow.fetch_token(code=query_params["code"])
            credentials = flow.credentials
            
            # Verify and decode Google OpenID encryption tokens
            info = id_token.verify_oauth2_token(
                credentials.id_token,
                google_requests.Request(),
                client_id
            )
            
            # Commit parameters into session state memory so login persists
            st.session_state.logged_in = True
            st.session_state.user = info.get("email")
            
            # CRITICAL: Clean URL parameters completely to avoid loop or state drop
            st.query_params.clear()
            st.success("Google Authentication Successful! 🚀")
            st.rerun()
            
        except Exception as e:
            st.error(f"Google Authorization Matrix Failure: {e}")


# ================= LOGIN =================
def firebase_login():

    st.markdown("### 🔐 Secure Login Portal")

    email = st.text_input("Email Address", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login 🚀"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)

            st.session_state.logged_in = True
            st.session_state.user = email

            st.success("Login Successful 🚀 Redirecting...")
            st.rerun()

        except Exception as e:
            st.error(f"Login Failed ❌ {e}")
            
    # ---- INTEGRATED GOOGLE AUTH FLOW TRIGGER ----
    google_login_component()


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
