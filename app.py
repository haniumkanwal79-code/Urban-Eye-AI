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
# 3. EXECUTIVE-LEVEL AUTH CSS (CLEAN, MINIMAL & STUNNING)
# =====================================================================
def load_executive_auth_css():
    st.markdown("""
    <style>
    /* Professional Modern Dashboard Block */
    .executive-card {
        background: linear-gradient(145deg, #0e1626 0%, #060b13 100%);
        border: 1px solid rgba(0, 229, 255, 0.18);
        padding: 30px;
        border-radius: 18px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), 0 0 25px rgba(0, 229, 255, 0.03);
        text-align: center;
        margin-bottom: 25px;
    }
    
    /* Clean Luxury Title */
    .brand-title {
        font-size: 40px;
        font-weight: 800;
        letter-spacing: 6px;
        color: #ffffff;
        margin: 0;
        text-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);
    }
    
    .brand-glow-tag {
        color: #00e5ff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 6px;
        text-shadow: 0 0 8px rgba(0, 229, 255, 0.3);
    }

    /* Slick Input Customization */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        color: #ffffff !important;
        font-size: 14px !important;
        transition: all 0.25s ease !important;
    }
    .stTextInput input:focus {
        border-color: #00e5ff !important;
        background-color: rgba(0, 229, 255, 0.02) !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.15) !important;
    }

    /* Input Box Top Labels styling */
    div[data-testid="stWidgetLabel"] p {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* Executive Styled Tabs List */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 4px !important;
        border-radius: 12px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border-radius: 9px !important;
        color: #64748b !important;
        padding: 12px 20px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00e5ff !important;
        color: #060b13 !important;
        box-shadow: 0 4px 12px rgba(0, 229, 255, 0.25) !important;
    }

    /* High-End Enterprise Button */
    .stButton button {
        background: linear-gradient(135deg, #00e5ff 0%, #00b4d8 100%) !important;
        color: #060b13 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 1.5px !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 20px !important;
        box-shadow: 0 4px 14px rgba(0, 229, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(0, 229, 255, 0.4) !important;
        background: linear-gradient(135deg, #00ffcc 0%, #00e5ff 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 4. PAGES & UI (FRONTEND AUTHENTICATION)
# =====================================================================

def show_auth_page():
    # Load safe luxury executive style injection
    load_executive_auth_css()
    
    # Header Panel Construction
    st.markdown('''
        <div class="executive-card">
            <h1 class="brand-title">URBAN EYE AI</h1>
            <div class="brand-glow-tag">⚡ Enterprise Control Center</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Secure Session Toggle
    keep_logged_in = st.checkbox("🔒 Keep control session active on this device", value=True, key="remember_me")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 SYSTEM ACCESSIBILITY", "📝 REQUEST OPERATOR CREDENTIALS"])

    # Email/Password Login
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        email = st.text_input("Clearance Email Address", key="l_email", placeholder="name@domain.com")
        password = st.text_input("Secure Access Password", type="password", key="l_password", placeholder="••••••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("AUTHORIZE SYSTEM SECURITY", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                
                if keep_logged_in:
                    st.query_params["session_user"] = email
                else:
                    st.query_params.clear()
                
                st.success("✅ Access sequence initiated. Syncing node logs...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Verification Failed: {e}")

    # Email/Password Signup
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        s_email = st.text_input("Operator Registration Email", key="s_email", placeholder="operator@domain.com")
        s_password = st.text_input("Create Encrypted Password", type="password", key="s_password", placeholder="Minimum 6 characters")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("REGISTER COMMAND PROFILE", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": s_email, "password": s_password})
                st.info("📨 Command node request forwarded! Switch to ACCESSIBILITY tab to log in.")
            except Exception as e:
                st.error(f"❌ Account Allocation Denied: {e}")

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
