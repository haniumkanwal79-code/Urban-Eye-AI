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
# 3. HIGH-OCTANE COLOR BLOCKS & NEON INTERFACE
# =====================================================================
def show_auth_page():
    # Injecting vibrant corporate cyberblocks & multi-color variables
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem !important;
            max-width: 580px !important;
        }
        
        /* Neon Gradient Brand Card */
        .brand-card-block {
            background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
            border-left: 5px solid #00e5ff;
            border-right: 5px solid #ff007f;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 25px;
            text-align: center;
        }
        
        h1.brand-header {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 900 !important;
            letter-spacing: 6px !important;
            background: linear-gradient(90deg, #00e5ff, #ff007f);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 !important;
        }
        
        .system-tagline {
            font-size: 12px !important;
            font-weight: 800 !important;
            letter-spacing: 2px !important;
            color: #00ffcc !important;
            margin-top: 8px;
        }

        /* Color Info Blocks */
        .cyan-info-block {
            background: rgba(0, 229, 255, 0.06);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            color: #e2e8f0;
            font-size: 13.5px;
            line-height: 1.5;
            margin-bottom: 20px;
        }
        
        .magenta-info-block {
            background: rgba(255, 0, 127, 0.06);
            border: 1px solid rgba(255, 0, 127, 0.2);
            border-radius: 10px;
            padding: 15px;
            color: #e2e8f0;
            font-size: 13.5px;
            line-height: 1.5;
            margin-bottom: 20px;
        }

        /* Vibrant Multi-Color Badges */
        .status-row {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 15px;
        }
        .badge {
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1px;
            padding: 6px 14px;
            border-radius: 6px;
            text-transform: uppercase;
        }
        .badge-electric { background: #00e5ff; color: #0f172a; box-shadow: 0 0 10px rgba(0, 229, 255, 0.4); }
        .badge-neon { background: #ff007f; color: #ffffff; box-shadow: 0 0 10px rgba(255, 0, 127, 0.4); }
        .badge-matrix { background: #00ffcc; color: #0f172a; box-shadow: 0 0 10px rgba(0, 255, 204, 0.4); }

        /* Navigation Tab Engine Styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #0f172a !important;
            padding: 6px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 11px !important;
            font-weight: 800 !important;
            letter-spacing: 1px !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            color: #64748b !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #00e5ff !important;
            border-bottom: 2px solid #00e5ff !important;
        }

        /* Input Controls Border Overrides */
        .stTextInput input {
            background-color: #090d16 !important;
            border: 1px solid rgba(0, 229, 255, 0.2) !important;
            border-radius: 8px !important;
            color: #ffffff !important;
        }
        .stTextInput input:focus {
            border-color: #ff007f !important;
            box-shadow: 0 0 8px rgba(255, 0, 127, 0.2) !important;
        }
        
        /* Vibrant Action Buttons */
        .stButton button {
            background: linear-gradient(90deg, #00e5ff 0%, #ff007f 100%) !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            letter-spacing: 2px !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 14px !important;
            box-shadow: 0 4px 15px rgba(255, 0, 127, 0.3) !important;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: scale(1.01) !important;
            box-shadow: 0 4px 25px rgba(0, 229, 255, 0.5) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. Main Premium Colored Hero Header Block
    st.markdown("""
        <div class="brand-card-block">
            <h1 class="brand-header">URBAN EYE AI</h1>
            <div class="system-tagline">✦ CORE SURVEILLANCE NODE CONTROL ✦</div>
            <div class="status-row">
                <span class="badge badge-electric">SYS: ONLINE</span>
                <span class="badge badge-neon">NODE: SECURE</span>
                <span class="badge badge-matrix">ENC: AES-256</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Checkbox configuration layer
    keep_logged_in = st.checkbox("Maintain structural authentication token on this hardware asset", value=True, key="remember_me")
    st.write(" ")
    
    # 2. Main Tabbed Environment
    tab1, tab2 = st.tabs(["⚡ INITIALIZE LOGIN MATRIX", "🛰️ ALLOCATE PROFILE LINK"])

    # Login panel
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        # Colored Context Block
        st.markdown("""
            <div class="cyan-info-block">
                <strong>🔵 INSTRUCTIONAL PROTOCOL:</strong><br>
                Please map your assigned network parameters. Entering incorrect verification logs will trigger a local workstation handshake timeout.
            </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("ENTER REGISTERED ROUTING IDENTIFIER (EMAIL)", key="l_email", placeholder="identity@domain.com")
        password = st.text_input("ENTER ACCESS ENCRYPTION MATRIX (PASSWORD)", type="password", key="l_password", placeholder="••••••••••••")
        st.write(" ")
        
        if st.button("EXECUTE SYSTEM ACCESSIBILITY AUTHENTICATION", use_container_width=True):
            if not supabase:
                st.error("Centralized routing cluster communication fault.")
                return
            with st.spinner("Decoding access array signals..."):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    
                    if keep_logged_in:
                        st.query_params["session_user"] = email
                    else:
                        st.query_params.clear()
                    
                    st.success("Verification successful. Initializing graphical terminal frames.")
                    st.rerun()
                except Exception:
                    st.error("Matrix error. Cryptographic credentials mismatch detected.")

    # Signup panel
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        # Colored Context Block
        st.markdown("""
            <div class="magenta-info-block">
                <strong>🔴 SECURITY NOTICE:</strong><br>
                Generating a new architecture environment registers a hard token footprint. Ensure you are provisioning via a secure, encrypted internal perimeter link.
            </div>
        """, unsafe_allow_html=True)
        
        s_email = st.text_input("TARGET ACCOUNT NODE REGISTRATION", key="s_email", placeholder="new_node@domain.com")
        s_password = st.text_input("DEFINE HARD ACCESS CODES", type="password", key="s_password", placeholder="Requires a minimum of 6 parameters")
        st.write(" ")
        
        if st.button("PROVISION NEW CORE OPERATOR CREDENTIALS", use_container_width=True):
            if not supabase:
                st.error("Centralized routing cluster communication fault.")
                return
            with st.spinner("Injecting structural identity values into secondary server arrays..."):
                try:
                    supabase.auth.sign_up({"email": s_email, "password": s_password})
                    st.info("💡 Provisioning sequence processed. Recalibrate input frames on the INITIALIZE LOGIN MATRIX tab.")
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
