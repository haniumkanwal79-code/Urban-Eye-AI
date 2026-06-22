import streamlit as st
from supabase import create_client, Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# =====================================================================
# 1. INITIALIZATION & CONNECTIONS
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

show_home_function = None
try:
    from home import show_home
    show_home_function = show_home
except ImportError:
    st.warning("⚠️ 'home.py' file not found! Using standard dashboard screen.")

# =====================================================================
# 2. EMAIL TRANSMISSION LOGIC
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
# 3. HIGH-END DESIGN & SIMPLE ENGLISH UI
# =====================================================================
def show_auth_page():
    # Premium CSS overrides for a beautiful tech UI layout
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2.5rem !important;
            max-width: 560px !important;
        }
        
        /* Sleek Premium Brand Top Card */
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
            letter-spacing: 2px !important;
            color: #00ffcc !important;
            margin-top: 6px;
            text-transform: uppercase;
        }

        /* Clean Colored Notification Blocks */
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

        /* Minimalist Status Pills */
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

        /* Modern Tabs Headers */
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

        /* Premium Input Fields Layout */
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
        
        /* Modern Gradient CTA Button */
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

    # 1. Main Header Box (Top-Level Styling)
    st.markdown("""
        <div class="premium-brand-card">
            <h1 class="brand-header">URBAN EYE AI</h1>
            <div class="system-tagline">✦ CONTROL DASHBOARD PORTAL ✦</div>
            <div class="status-row">
                <span class="status-pill pill-highlight">● SYSTEM: ONLINE</span>
                <span class="status-pill">SECURE CONNECTION</span>
                <span class="status-pill">VERSION 2.4</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Remember login checkbox
    keep_logged_in = st.checkbox("Keep me logged in on this device", value=True, key="remember_me")
    st.write(" ")
    
    # 2. Workspace Navigation Tabs
    tab1, tab2 = st.tabs(["✦ SIGN IN", "✦ CREATE ACCOUNT"])

    # Login Container
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="panel-info-box">
                <strong>WELCOME BACK:</strong><br>
                Please enter your email and password below to log into your dashboard room securely.
            </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("Email Address", key="l_email", placeholder="username@domain.com")
        password = st.text_input("Password", type="password", key="l_password", placeholder="••••••••••••")
        st.write(" ")
        
        if st.button("LOG IN TO SYSTEM", use_container_width=True):
            if not supabase:
                st.error("Database connection is currently offline.")
                return
            with st.spinner("Checking your account details..."):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    
                    if keep_logged_in:
                        st.query_params["session_user"] = email
                    else:
                        st.query_params.clear()
                    
                    st.success("Login successful! Loading your dashboard...")
                    st.rerun()
                except Exception:
                    st.error("Login failed. Please check your email or password.")

    # Signup Container
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="panel-info-box" style="border-left-color: #ff007f;">
                <strong style="color: #ff007f;">NEW REGISTRATION:</strong><br>
                Create a new account here to gain access. All accounts require a secure login process.
            </div>
        """, unsafe_allow_html=True)
        
        s_email = st.text_input("Your Email Address", key="s_email", placeholder="newuser@domain.com")
        s_password = st.text_input("Choose a Password", type="password", key="s_password", placeholder="Must be at least 6 characters")
        st.write(" ")
        
        if st.button("REGISTER ACCOUNT", use_container_width=True):
            if not supabase:
                st.error("Database connection is currently offline.")
                return
            with st.spinner("Creating your profile setup..."):
                try:
                    supabase.auth.sign_up({"email": s_email, "password": s_password})
                    st.info("💡 Registration successful! Please switch back to the SIGN IN tab to log in.")
                except Exception as e:
                    st.error(f"Could not create account. Error details: {e}")

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
            st.success(f"Active Session: {st.session_state.user.email}")
            if st.button("Log Out"):
                st.session_state.user = None
                st.query_params.clear()
                st.rerun()

if __name__ == "__main__":
    main()
