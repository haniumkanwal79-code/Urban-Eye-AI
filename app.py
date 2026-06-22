import streamlit as st
import os
import sys
from supabase import create_client, Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# =====================================================================
# 1. PATH RESOLVER (Important for Deployment)
# =====================================================================
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# =====================================================================
# 2. INITIALIZATION & CONNECTIONS
# =====================================================================
SUPABASE_URL = "https://mrwkglukekmikenihkfp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yd2tnbHVrZWttaWtlbmloa2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDQwODgsImV4cCI6MjA5NzcyMDA4OH0.Y1UpomD34O8shloIV6OGVFET5BFVfawLk2yDJZQy8yM"

if "supabase_client" not in st.session_state:
    try:
        st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Database Connection Error: {e}")

supabase = st.session_state.get("supabase_client", None)
if "user" not in st.session_state:
    st.session_state.user = None

# IMPORT HOME.PY
show_home_function = None
try:
    from home import show_home
    show_home_function = show_home
except ImportError:
    st.warning("⚠️ 'home.py' not found in root directory!")

# =====================================================================
# 3. EMAIL & UI FUNCTIONS
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
        return False

def show_auth_page():
    st.markdown("""
        <style>
        .premium-brand-card { background: linear-gradient(135deg, #090d16 0%, #111827 100%); border-top: 4px solid #00e5ff; padding: 30px; border-radius: 16px; text-align: center; }
        h1.brand-header { font-weight: 800 !important; color: #ffffff !important; }
        .stButton button { background: linear-gradient(93deg, #00e5ff 0%, #00b4d8 100%) !important; color: #090d16 !important; font-weight: 700 !important; border-radius: 10px !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="premium-brand-card"><h1 class="brand-header">URBAN EYE AI</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✦ SIGN IN", "✦ CREATE ACCOUNT"])

    with tab1:
        email = st.text_input("Email", key="l_email")
        password = st.text_input("Password", type="password", key="l_password")
        if st.button("LOG IN"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.rerun()
            except:
                st.error("Login failed.")

    with tab2:
        s_email = st.text_input("Email", key="s_email")
        s_password = st.text_input("Password", type="password", key="s_password")
        if st.button("REGISTER"):
            try:
                supabase.auth.sign_up({"email": s_email, "password": s_password})
                st.info("Check your email for verification.")
            except Exception as e:
                st.error(f"Error: {e}")

# =====================================================================
# 4. ROUTER
# =====================================================================
def main():
    if st.session_state.user is None:
        show_auth_page()
    else:
        if show_home_function:
            show_home_function()
        else:
            st.error("Dashboard (home.py) missing.")

if __name__ == "__main__":
    main()
