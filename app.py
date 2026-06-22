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

# 🟢 Safely import your home dashboard function
show_home_function = None
try:
    from home import show_home
    show_home_function = show_home
except ImportError:
    st.warning("⚠️ 'home.py' file not found! But the login screen is active.")

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
# 3. FRESH & SIMPLE ENGLISH UI (WITH AWESOME GESTURES)
# =====================================================================
def show_auth_page():
    # Crisp titles with a friendly pop
    st.markdown("<h1 style='text-align: center; color: #00e5ff;'>🏛️ URBAN EYE AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #00ffcc;'>👋 Welcome to the Control Center!</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8892b0; font-size: 14px;'>Manage your area surveillance and reports easily</p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid #00e5ff;'>", unsafe_allow_html=True)
    
    # Simple Keep me logged in checkbox text
    keep_logged_in = st.checkbox("🔒 Remember me on this device (Skip login next time!)", value=True, key="remember_me")
    
    st.write(" ")
    
    # Modern active tabs
    tab1, tab2 = st.tabs(["🔑 LOG IN TO YOUR ACCOUNT", "📝 CREATE NEW ACCOUNT"])

    # Email/Password Login
    with tab1:
        st.markdown("<br><h4 style='color: #00e5ff;'>👋 Hello Officer! Enter your email and password:</h4>", unsafe_allow_html=True)
        email = st.text_input("📧 Your Email Address", key="l_email", placeholder="you@example.com")
        password = st.text_input("🔒 Your Password", type="password", key="l_password", placeholder="Type your password here...")
        st.write(" ")
        
        if st.button("🚀 ENTER THE SYSTEM", use_container_width=True):
            if not supabase:
                st.error("❌ Supabase connection is down.")
                return
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                
                if keep_logged_in:
                    st.query_params["session_user"] = email
                else:
                    st.query_params.clear()
                
                st.success("🎉 Awesome! Credentials verified. Taking you inside...")
                st.rerun()
            except Exception as e:
                st.error("❌ Login failed! Please check if your email or password is correct.")

    # Email/Password Signup
    with tab2:
        st.markdown("<br><h4 style='color: #00ffcc;'>🆕 New here? Fill this up to sign up:</h4>", unsafe_allow_html=True)
        s_email = st.text_input("📧 New Email Address", key="s_email", placeholder="Type your email here...")
        s_password = st.text_input("🔒 Choose a Strong Password", type="password", key="s_password", placeholder="At least 6 characters long")
        st.write(" ")
        
        if st.button("✨ CREATE ACCOUNT NOW", use_container_width=True):
            if not supabase:
                st.error("❌ Supabase connection is down.")
                return
            try:
                supabase.auth.sign_up({"email": s_email, "password": s_password})
                st.info("📨 Congratulations! Your account has been made. Now switch to the LOG IN tab above to log in! 👉")
            except Exception as e:
                st.error(f"❌ Couldn't create account. Error: {e}")

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
            st.success(f"🥳 You are successfully logged in as: {st.session_state.user.email}")
            if st.button("Log Out 🚪"):
                st.session_state.user = None
                st.query_params.clear()
                st.rerun()

if __name__ == "__main__":
    main()
