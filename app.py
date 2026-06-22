import streamlit as st
from supabase import create_client, Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

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

# 🟢 home.py se exact control center panel function ko import karna safely
try:
    from home import show_home
except ImportError:
    st.error("❌ 'home.py' file nahi mili! Kindly check karein ke dono files aik hi folder me hain.")

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
# 3. ULTRA-PREMIUM PURE CSS INJECTION (SAFE & STUNNING)
# =====================================================================
def load_luxury_auth_css():
    st.markdown("""
    <style>
    /* Glowing Title Box */
    .premium-header {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.05) 0%, rgba(0, 255, 204, 0.02) 100%);
        border: 1px solid rgba(0, 229, 255, 0.2);
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0px 10px 30px rgba(0, 229, 255, 0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Cyber Title Neon Animation Text */
    .portal-main-title {
        font-size: 46px;
        font-weight: 900;
        letter-spacing: 5px;
        background: linear-gradient(90deg, #ffffff, #00e5ff, #00ffcc, #ffffff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 4s linear infinite;
        margin: 0;
    }
    
    .portal-sub-text {
        color: #8892b0;
        font-size: 14px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 8px;
    }

    /* Input Fields Border Styling */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        transition: all 0.3s ease-in-out !important;
    }
    .stTextInput input:focus {
        border-color: #00ffcc !important;
        box-shadow: 0px 0px 15px rgba(0, 255, 204, 0.3) !important;
    }

    /* Style Streamlit Input Labels */
    div[data-testid="stWidgetLabel"] p {
        color: #00e5ff !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }

    /* Customizing Streamlit Tabs Header to look like an app dashboard */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 5px !important;
        border-radius: 12px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border-radius: 8px !important;
        color: #8892b0 !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.2) 0%, rgba(0, 255, 204, 0.1) 100%) !important;
        border: 1px solid #00e5ff !important;
        color: #00e5ff !important;
    }

    /* Luxurious Glowing Login Button */
    .stButton button {
        background: linear-gradient(90deg, #00e5ff 0%, #00ffcc 100%) !important;
        color: #030712 !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        letter-spacing: 2px !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 24px !important;
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.3) !important;
        transition: all 0.3s ease-in-out !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 30px rgba(0, 255, 204, 0.6) !important;
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 4. PAGES & UI (FRONTEND AUTHENTICATION)
# =====================================================================

def show_auth_page():
    # Load safe luxury style injection
    load_luxury_auth_css()
    
    # Header Neon Card Wrapper
    st.markdown('''
        <div class="premium-header">
            <h1 class="portal-main-title">URBAN EYE AI</h1>
            <div class="portal-sub-text">👁️ Secure Surveillance Node Access</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Keep me logged in session widget
    keep_logged_in = st.checkbox("🔒 Keep command node session active", value=True, key="remember_me")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 AUTHORIZED LOGIN", "📝 OFFICER REGISTRATION"])

    # Email/Password Login
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        email = st.text_input("📡 Clearance Email Address", key="l_email", placeholder="officer@agency.gov")
        password = st.text_input("🗝️ Access Token / Password", type="password", key="l_password", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("AUTHENTICATE & GRANT ENTRY", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                
                if keep_logged_in:
                    st.query_params["session_user"] = email
                else:
                    st.query_params.clear()
                
                st.success("✅ Signature verified. Initializing secure dashboard...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Verification Failed: {e}")

    # Email/Password Signup
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        s_email = st.text_input("📧 Terminal Request Email", key="s_email", placeholder="your-identity@domain.com")
        s_password = st.text_input("🔒 Construct Master Password", type="password", key="s_password", placeholder="Minimum 6 characters")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("GENERATE INTEL ACCOUNT", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": s_email, "password": s_password})
                st.info("📨 Node creation code initialized! Switch to LOGIN tab to activate clearance.")
            except Exception as e:
                st.error(f"❌ Registration Blocked: {e}")

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
