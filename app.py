import streamlit as st
from supabase import create_client, Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# 🟢 home.py se exact control center panel function ko import karna safely
try:
    from home import show_home
except ImportError:
    st.error("❌ 'home.py' file nahi mili! Kindly check karein ke dono files aik hi folder me hain.")

# =====================================================================
# 1. CONFIGURATION & CONNECTIONS
# =====================================================================

SUPABASE_URL = "https://mrwkglukekmikenihkfp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yd2tnbHVrZWttaWtlbmloa2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDQwODgsImV4cCI6MjA5NzcyMDA4OH0.Y1UpomD34O8shloIV6OGVFET5BFVfawLk2yDJZQy8yM"

if "supabase_client" not in st.session_state:
    st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = st.session_state.supabase_client

if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================================
# 2. EMAIL SENDING LOGIC (BACKEND REVENUE)
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
# 3. PREMIUM UI STYLING (ONLY FOR AUTH PAGE)
# =====================================================================
def load_auth_css():
    st.markdown("""
    <style>
    /* Gradient Background for Portal */
    .stApp {
        background: radial-gradient(circle at center, #0f172a 0%, #050814 100%) !important;
    }
    
    /* Center Card Custom Styling */
    .auth-container {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(16px);
        padding: 35px;
        border-radius: 20px;
        border: 1px solid rgba(0, 229, 255, 0.2);
        box-shadow: 0px 0px 40px rgba(0, 229, 255, 0.15);
        margin-bottom: 25px;
    }
    
    /* Main Portal Heading */
    .portal-title {
        font-size: 38px;
        font-weight: 800;
        color: #00e5ff;
        text-align: center;
        letter-spacing: 2px;
        text-shadow: 0px 0px 15px rgba(0, 229, 255, 0.5);
        margin-bottom: 5px;
    }
    
    .portal-subtitle {
        color: #a9c4d8;
        text-align: center;
        font-size: 15px;
        margin-bottom: 20px;
    }
    
    /* Premium Buttons Customization */
    .stButton button {
        background: linear-gradient(90deg, #00e5ff, #00ffcc) !important;
        color: #050814 !important;
        font-weight: bold !important;
        letter-spacing: 1px;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
        transition: 0.3s ease-in-out !important;
    }
    
    .stButton button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0px 0px 20px rgba(0, 255, 204, 0.6) !important;
    }
    
    /* Tabs Styling adjustment */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #ffffff;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 229, 255, 0.15) !important;
        border: 1px solid #00e5ff !important;
        color: #00e5ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 4. PAGES & UI (FRONTEND AUTHENTICATION)
# =====================================================================

def show_auth_page():
    # Premium Styles Inject karein
    load_auth_css()
    
    # Visual Box Structure container
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<div class="portal-title">🏛️ URBAN EYE AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="portal-subtitle">National Intelligence & Surveillance Access Portal</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-Login Checkbox (Clean UI Placement)
    keep_logged_in = st.checkbox("🔄 Keep me logged in permanently", value=True, key="remember_me")
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Authorized Login", "📝 Officer Registration"])

    # Email/Password Login
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        email = st.text_input("🛡️ Registered Email Address", key="l_email", placeholder="Enter official email...")
        password = st.text_input("🔑 Access Password", type="password", key="l_password", placeholder="Enter secure password...")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("AUTHENTICATE & ENTER SYSTEM", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                
                if keep_logged_in:
                    st.query_params["session_user"] = email
                else:
                    st.query_params.clear()
                
                st.success("✅ Credentials verified! Access granted.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Authentication Failed: {e}")

    # Email/Password Signup
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        s_email = st.text_input("📧 Request Account Email", key="s_email", placeholder="Enter your email address...")
        s_password = st.text_input("🔒 Generate Access Password", type="password", key="s_password", placeholder="Create strong password...")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("INITIALIZE COMMAND ACCOUNT", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": s_email, "password": s_password})
                st.info("📨 Account creation request initialized! You can now switch to the login tab to log in.")
            except Exception as e:
                st.error(f"❌ Signup Failed: {e}")

# =====================================================================
# 5. CONTROL CONTROLLER (MAIN APP TRIGGER & ROUTING)
# =====================================================================
def main():
    url_params = st.query_params.to_dict()
    
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
        # Main Dashboard running panel
        show_home()
        
        # Logout catch engine
        if st.session_state.user is None:
            st.query_params.clear() 
            st.rerun()

if __name__ == "__main__":
    main()
