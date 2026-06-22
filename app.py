import streamlit as st
from supabase import create_client, Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# =====================================================================
# 1. CONFIGURATION & CONNECTIONS (SAFE INIT)
# =====================================================================
SUPABASE_URL = "https://mrwkglukekmikenihkfp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yd2tnbHVrZWttaWtlbmloa2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDQwODgsImV4cCI6MjA5NzcyMDA4OH0.Y1UpomD34O8shloIV6OGVFET5BFVfawLk2yDJZQy8yM"

if "supabase_client" not in st.session_state:
    try:
        st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase Connection Error: {e}")

supabase = st.session_state.get("supabase_client", None)

if "user" not in st.session_state:
    st.session_state.user = None

# Safely import your home dashboard function
show_home_function = None
try:
    from home import show_home
    show_home_function = show_home
except ImportError:
    st.warning("⚠️ 'home.py' file not found! Standard dashboard fallback active.")

# =====================================================================
# 2. EMAIL SENDING LOGIC (UNTOUCHED)
# =====================================================================
def send_report_email(to_email, subject, body, attachment_path=None):
    sender_email = "your_email@gmail.com" 
    sender_password = "your_app_password_here" 

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        msg.attach(part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

# =====================================================================
# 3. HIGH-END UI STYLING & STRUCTURE
# =====================================================================
def show_auth_page():
    # Injecting modern focused CSS overrides safely
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: 600 !important;
            letter-spacing: 0.5px;
            padding: 10px 20px !important;
        }
        div[data-testid="stMarkdownContainer"] h1 {
            font-weight: 800 !important;
            letter-spacing: 3px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Clean, sophisticated Header
    st.markdown("<h1 style='text-align: center; color: #ffffff; margin-bottom: 5px;'>URBAN EYE AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00e5ff; font-size: 15px; font-weight: 600; letter-spacing: 1px; margin-top: 0px;'>✦ CONTROL DASHBOARD PORTAL ✦</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px; margin-top: -10px;'>Secure infrastructure for localized area surveillance and analysis</p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 0.5px solid rgba(255, 255, 255, 0.15); margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # Clean Session Checkbox
    keep_logged_in = st.checkbox("Keep me logged in on this workstation", value=True, key="remember_me")
    
    st.write(" ")
    
    # Structured Professional Tabs
    tab1, tab2 = st.tabs(["■ SYSTEM SIGN-IN", "■ CREATE OPERATOR ACCOUNT"])

    # Email/Password Login
    with tab1:
        st.markdown("<br><p style='color: #ffffff; font-size: 15px; font-weight: 500;'>Please verify your credentials to access the node:</p>", unsafe_allow_html=True)
        email = st.text_input("Registered Email Address", key="l_email", placeholder="username@domain.com")
        password = st.text_input("Account Password", type="password", key="l_password", placeholder="••••••••••••")
        st.write(" ")
        
        if st.button("AUTHENTICATE ACCESS", use_container_width=True):
            if not supabase:
                st.error("Authentication system link is currently offline.")
                return
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                
                if keep_logged_in:
                    st.query_params["session_user"] = email
                else:
                    st.query_params.clear()
                
                st.success("Credentials authenticated successfully. Loading dashboard panels...")
                st.rerun()
            except Exception as e:
                st.error("Authentication failed. Please verify your email and password entry.")

    # Email/Password Signup
    with tab2:
        st.markdown("<br><p style='color: #ffffff; font-size: 15px; font-weight: 500;'>Register a new terminal user profile below:</p>", unsafe_allow_html=True)
        s_email = st.text_input("Desired Email Account", key="s_email", placeholder="newuser@domain.com")
        s_password = st.text_input("Secure Password Configuration", type="password", key="s_password", placeholder="Minimum of 6 characters required")
        st.write(" ")
        
        if st.button("REGISTER OPERATOR PROFILE", use_container_width=True):
            if not supabase:
                st.error("Authentication system link is currently offline.")
                return
            try:
                supabase.auth.sign_up({"email": s_email, "password": s_password})
                st.info("💡 Registration request processed successfully. Please navigate back to the SYSTEM SIGN-IN tab to enter.")
            except Exception as e:
                st.error(f"Unable to process registration profile. System reason: {e}")

# =====================================================================
# 4. CONTROL CONTROLLER (ROUTING & TRIGGER)
# =====================================================================
def main():
    try:
        url_params = st.query_params.to_dict()
    except Exception:
        url_params = {}
    
    # Background Auto-Login Layer
    if "session_user" in url_params and st.session_state.user is None:
        class DummyUser:
            def __init__(self, email):
                self.email = email
        st.session_state.user = DummyUser(url_params["session_user"])

    # Routing Logic
    if st.session_state.user is None:
        show_auth_page()
    else:
        if show_home_function:
            show_home_function()
        else:
            st.success(f"Session Active: {st.session_state.user.email}")
            if st.button("Terminate Session"):
                st.session_state.user = None
                st.query_params.clear()
                st.rerun()

if __name__ == "__main__":
    main()
