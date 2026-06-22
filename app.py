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
# 3. ADVANCED FUTURISTIC UI STYLING (THE ULTIMATE OVERHAUL)
# =====================================================================
def load_advanced_auth_css():
    st.markdown("""
    <style>
    /* Full Page Cyber Background */
    .stApp {
        background: radial-gradient(circle at center, #0a1128 0%, #030712 100%) !important;
    }
    
    /* Main Card Frame with Animation */
    .auth-card {
        background: rgba(10, 25, 47, 0.45);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 0 50px rgba(0, 229, 255, 0.1), inset 0 0 20px rgba(0, 229, 255, 0.05);
        text-align: center;
        transition: all 0.5s ease;
    }
    .auth-card:hover {
        border-color: rgba(0, 255, 204, 0.45);
        box-shadow: 0 0 60px rgba(0, 255, 204, 0.15), inset 0 0 30px rgba(0, 255, 204, 0.05);
    }
    
    /* Elegant Badge Above Title */
    .system-badge {
        display: inline-block;
        padding: 6px 14px;
        background: rgba(0, 229, 255, 0.1);
        border: 1px solid rgba(0, 229, 255, 0.4);
        border-radius: 50px;
        color: #00e5ff;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    
    /* Cyber Title & Neon Glow */
    .portal-main-title {
        font-size: 45px;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 30%, #00e5ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 4px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    
    .portal-sub-text {
        color: #8892b0;
        font-size: 15px;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }

    /* Style Streamlit Input Labels to Match Cyber Theme */
    div[data-testid="stWidgetLabel"] p {
        color: #00e5ff !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }

    /* Customizing Streamlit Tabs Header */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 6px !important;
        border-radius: 14px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        border-radius: 10px !important;
        color: #8892b0 !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.2) 0%, rgba(0, 255, 204, 0.1) 100%) !important;
        border: 1px solid rgba(0, 229, 255, 0.5) !important;
        color: #00e5ff !important;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
    }

    /* Ultimate Glowing Action Button */
    .stButton button {
        background: linear-gradient(90deg, #00e5ff 0%, #00ffcc 100%) !important;
        color: #020c1b !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        letter-spacing: 2px !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 14px 28px !important;
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.25) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 30px rgba(0, 255, 204, 0.5) !important;
    }
    
    /* Make checkboxes look integrated */
    .stCheckbox {
        color: #ccd6f6 !important;
    }
    </style>
    """, unsafe_allow_html=True)
