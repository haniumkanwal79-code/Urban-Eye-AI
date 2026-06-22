import streamlit as st
from supabase import create_client, Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# =====================================================================
# 1. INITIALIZATION & STABLE CONNECTIONS
# =====================================================================
SUPABASE_URL = "https://mrwkglukekmikenihkfp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yd2tnbHVrZWttaWtlbmloa2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDQwODgsImV4cCI6MjA5NzcyMDA4OH0.Y1UpomD34O8shloIV6OGVFET5BFVfawLk2yDJZQy8yM"

if "supabase_client" not in st.session_state:
    try:
        st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"System Matrix Connectivity Error: {e}")

supabase = st.session_state.get("supabase_client", None)

if "user" not in st.session_state:
    st.session_state.user = None

show_home_function = None
try:
    from home import show_home
    show_home_function = show_home
except ImportError:
    st.warning("⚠️ Core routing module 'home.py' offline. Running staging bypass container.")

# =====================================================================
# 2. EMAIL AUTOMATION ENGINE
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
        print(f"SMTP Transmission Fault: {e}")
        return False

# =====================================================================
# 3. BALANCED PREMIUM HIGH-TECH COLOR BLOCKS
# =====================================================================
def show_auth_page():
    # Elite enterprise styling layout
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2.5rem !important;
            max-width: 560px !important;
        }
        
        /* Premium Minimal Executive Block */
        .premium-brand-card {
            background: linear-gradient(135deg, #090d16 0%, #111827 100%);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-top: 4px solid #00e5ff;
            padding: 30px 25px;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
            margin-bottom: 25px;
            text-align: center;
        }
        
        h1.brand-header {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-weight: 800 !important;
            letter-spacing: 5px !important;
            color: #ffffff !important;
            margin: 0 !important;
        }
        
        .system-tagline {
            font-size: 11px !important;
            font-weight: 700 !important;
            letter-spacing: 2.5px !important;
            color: #00ffcc !important;
            margin-top: 6px;
            text-transform: uppercase;
        }

        /* Sophisticated Executive Color Blocks */
        .panel-info-box {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-left: 4px solid #00e5ff;
            border-radius: 12px;
            padding: 16px 20px;
            color: #94a3b8;
            font-size: 13.5px;
            line-height: 1.6;
            margin-bottom: 25px;
        }
        
        .panel-info-box strong {
            color: #ffffff;
            font-weight: 600;
        }

        /* Premium Minimalist Status Tags */
        .status-row {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 18px;
        }
        .status-pill {
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            padding: 5px 12px;
            border-radius: 6px;
            text-transform: uppercase;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #cbd5e1;
        }
        .pill-highlight {
            color: #00ffcc;
            border-color: rgba(0, 255, 204, 0.2);
            background: rgba(0, 255, 204, 0.02);
        }

        /* Modernized Tabs Headers */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
            gap: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 12px !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            color: #64748b !important;
            text-transform: uppercase;
            padding: 12px 4px !important;
        }
        .stTabs [aria-selected="true"] {
            color: #00e5ff !important;
            border-bottom: 2px solid #00e5ff !important;
        }

        /* Executive Input Fields Styling */
        div[data-testid="stWidgetLabel"] p {
            color: #e2e8f0 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            letter-spacing: 0.5px;
        }
        .stTextInput input {
            background-color: #090d16 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            padding: 12px !important;
            color: #ffffff !important;
            transition: all 0.2s ease;
        }
        .stTextInput input:focus {
            border-color: #00e5ff !important;
            box-shadow: 0 0 0 1px #00e5ff !important;
        }
        
        /* Clean Premium Action Button */
        .stButton button {
            background: linear-gradient(93deg, #00e5ff 0%, #00b4d8 100%) !important;
            color: #090d16 !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            letter-spacing: 1.5px !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 14px !important;
            box-shadow: 0 4px 20px rgba(0, 229, 255, 0.15) !important;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            background: linear-gradient(93deg, #00ffcc 0%, #00e5ff 100%) !important;
            box-shadow: 0 4px 25px rgba(0, 255, 204, 0.3) !important;
            transform: translateY(-0.5px);
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. Main Header Container (Corporate Cyber-Style)
    st.markdown("""
        <div class="premium-brand-card">
            <h1 class="brand-header">URBAN EYE AI</h1>
            <div class="system-tagline">✦ CORE SURVEILLANCE MATRIX ✦</div>
            <div class="status-row">
                <span class="status-pill pill-highlight">● SYSTEM: ONLINE</span>
                <span class="status-pill">NODE: SECURE</span>
                <span class="status-pill">PORTAL: v2.4</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Session Persistence Selection
    keep_logged_in = st.checkbox("Maintain secure system authorization token on this workstation", value=True, key="remember_me")
    st.write(" ")
    
    # 2. Main Tabbed Workspace
    tab1, tab2 = st.tabs(["✦ SYSTEM SIGN-IN", "✦ ENROLL TERMINAL NODE"])

    # Authentication Tab
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="panel-info-box">
                <strong>SECURE NODE ACCESS:</strong><br>
                Please provide authorized routing logs to sync telemetry. Unauthorized intrusion attempts are recorded under terminal audit protocols.
            </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("Operator Identifier (Email Address)", key="l_email", placeholder="username@domain.com")
        password = st.text_input("Cryptographic Access Key (Password)", type="password", key="l_password", placeholder="••••••••••••")
        st.write(" ")
        
        if st.button("INITIALIZE SECURE SIGN-IN SEQUENCE", use_container_width=True):
            if not supabase:
                st.error("Centralized routing cluster communication fault.")
                return
            with st.spinner("Processing network decryption tokens..."):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    
                    if keep_logged_in:
                        st.query_params["session_user"] = email
                    else:
                        st.query_params.clear()
                    
                    st.success("Credentials authenticated. Initializing interface frames...")
                    st.rerun()
                except Exception:
                    st.error("Authentication rejected. Invalid credentials or network signature error.")

    # Signup Tab
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="panel-info-box" style="border-left-color: #ff007f;">
                <strong style="color: #ff007f;">OPERATOR PROVISIONING:</strong><br>
                Deploy structural parameters to request a primary node linkage. All profiles require automated cryptographic activation signatures.
            </div>
        """, unsafe_allow_html=True)
        
        s_email = st.text_input("Target Registration Domain", key="s_email", placeholder="new_node@domain.com")
        s_password = st.text_input("Define Encryption Parameters", type="password", key="s_password", placeholder="Minimum of 6 alphanumeric characters")
        st.write(" ")
        
        if st.button("PROVISION ARCHITECTURE PROFILE", use_container_width=True):
            if not supabase:
                st.error("Centralized routing cluster communication fault.")
                return
            with st.spinner("Injecting registration parameters into master cluster..."):
                try:
                    supabase.auth.sign_up({"email": s_email, "password": s_password})
                    st.info("💡 Provisioning successful. Re-route via the SYSTEM SIGN-IN matrix component.")
                except Exception as e:
                    st.error(f"Allocation procedure terminated. Structural validation crash: {e}")

# =====================================================================
# 4. MONITOR ENGINE ROUTER
# =====================================================================
def main():
    try:
        url_params = st.query_params.to_dict()
    except Exception:
        url_params = {}
    
    if "session_user" in url_params and st.session_state.user is None:
        class DummyUser:
            def __init__(self, email):
                self.email = email
        st.session_state.user = DummyUser(url_params["session_user"])

    if st.session_state.user is None:
        show_auth_page()
    else:
        if show_home_function:
            show_home_function()
        else:
            st.success(f"Session Token Validated: {st.session_state.user.email}")
            if st.button("De-Authorize Endpoint"):
                st.session_state.user = None
                st.query_params.clear()
                st.rerun()

if __name__ == "__main__":
    main()
