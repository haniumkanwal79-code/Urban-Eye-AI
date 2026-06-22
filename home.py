import os
import time
import smtplib
from datetime import datetime
import cv2
import numpy as np
import pandas as pd
import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# Email libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Gemini SDK
try:
    from google import genai
except ImportError:
    st.error("Please install the new Google GenAI library using: pip install google-genai")

# ================= PAGE CONFIG =================
def init_page_config():
    try:
        st.set_page_config(
            page_title="Urban Eye AI - Control Center",
            page_icon="👁️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except Exception:
        pass

@st.cache_resource
def load_yolo_model():
    return YOLO("best.pt")

try:
    model = load_yolo_model()
except Exception:
    model = None

# ================= HIGH-END EXECUTIVE CSS =================
def load_css():
    st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; }
    .premium-brand-card {
        background: linear-gradient(135deg, #090d16 0%, #111827 100%);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-top: 4px solid #00e5ff;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        margin-bottom: 30px;
        text-align: center;
    }
    h1.brand-header { font-weight: 800 !important; letter-spacing: 4px !important; color: #ffffff !important; }
    .system-tagline { font-size: 11px !important; font-weight: 700 !important; letter-spacing: 2px !important; color: #00ffcc !important; text-transform: uppercase; }
    .dashboard-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.06); padding: 22px; border-radius: 14px; color: #94a3b8; font-size: 12px; font-weight: 700; text-transform: uppercase; text-align: center; }
    .metric-value { font-size: 32px !important; font-weight: 800 !important; color: #ffffff !important; margin-top: 5px; }
    .panel-info-box { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #00e5ff; border-radius: 12px; padding: 16px 20px; color: #94a3b8; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# ================= AI GENERATION SYSTEM (GEMINI LLM) =================
def generate_ai_action_plan(issue_type, location):
    try:
        api_key = st.secrets["gemini"]["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        prompt = f"Issue: {issue_type} at {location}. Provide 3 professional, concise bullet points for field dispatch. Max 60 words."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except:
        return f"Standard deployment for {issue_type} at {location}. Secure area, assess damage, and initiate repair protocols."

# ================= EMAIL SYSTEM =================
def send_report_email(department_email, issue_type, location, timestamp, pdf_path, ai_plan):
    try:
        sender_email = st.secrets["email"]["SENDER_EMAIL"]
        sender_password = st.secrets["email"]["APP_PASSWORD"]
    except:
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = department_email
    msg['Subject'] = f"🚨 URGENT: Official Urban Intelligence Alert - {issue_type.upper()}"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; border: 1px solid #e0e0e0; padding: 25px; border-radius: 12px; max-width: 600px; background-color: #ffffff;">
        <h2 style="color: #090d16; border-bottom: 3px solid #00e5ff; padding-bottom: 10px;">Urban Eye AI: Incident Alert</h2>
        <p>Dear Department Head,</p>
        <p>A new urban hazard has been detected by the <b>National Urban Intelligence System</b>.</p>
        <div style="background-color: #f8fafc; padding: 15px; border-left: 5px solid #00e5ff; margin: 20px 0;">
            <p><b>Issue Type:</b> {issue_type.upper()}</p>
            <p><b>Location Zone:</b> {location}</p>
            <p><b>Timestamp:</b> {timestamp}</p>
        </div>
        <h3 style="color: #334155;">📋 Field Action Plan:</h3>
        <p style="color: #475569;">{ai_plan.replace('•', '•')}</p>
        <hr style="border: 0; border-top: 1px solid #eee;">
        <p style="font-size: 11px; color: #94a3b8;">This is an automated encrypted transmission. Refer to the attached PDF for official compliance reporting.</p>
    </div>
    """
    msg.attach(MIMEText(html_body, 'html'))

    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename=Report_{issue_type}.pdf")
            msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, department_email, msg.as_string())
    server.quit()
    return True

# ================= REPORT SYSTEM =================
def generate_report(issue_type, location, image_path):
    from pdf_utils import create_pdf
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ai_plan = generate_ai_action_plan(issue_type, location)
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%); border-left: 5px solid #00e5ff; padding: 20px; border-radius: 0 10px 10px 0; margin: 20px 0;">
        <h4 style="color: #00e5ff; margin-top: 0;">🚀 AI DEPLOYMENT STRATEGY</h4>
        <div style="color: #f1f5f9; font-size: 15px; line-height: 1.8;">{ai_plan}</div>
    </div>
    """, unsafe_allow_html=True)

    pdf_path = create_pdf(issue_type, location, image_path, timestamp)
    
    if "incident_db" not in st.session_state: st.session_state.incident_db = []
    st.session_state.incident_db.append({"id": f"UE-{1000+len(st.session_state.incident_db)}", "type": issue_type, "location": location, "timestamp": timestamp, "status": "🔴 Pending", "action_plan": ai_plan})
    
    target_email = {"road": "road.maintenance@government.gov", "garbage": "waste.management@government.gov"}.get(issue_type.lower(), "central.command@government.gov")
    if send_report_email(target_email, issue_type, location, timestamp, pdf_path, ai_plan):
        st.success(f"🚀 Report routed to {target_email}")

# ================= DASHBOARD & REST OF APP =================
def dashboard():
    st.markdown('<div class="premium-brand-card"><h1 class="brand-header">URBAN EYE AI</h1><div class="system-tagline">✦ LIVE MONITORING & ENFORCEMENT center ✦</div></div>', unsafe_allow_html=True)
    # Add your existing logic here...

def upload_section():
    # Add your existing logic here...
    pass

def show_home():
    if "incident_db" not in st.session_state: st.session_state.incident_db = []
    load_css()
    menu = st.sidebar.radio("🏛 CONTROL CENTER", ["🏛 Dashboard", "📡 Surveillance Grid", "📊 Analytics", "📋 Track Submissions", "⚙️ Settings"])
    if menu == "🏛 Dashboard": dashboard()
    elif menu == "📡 Surveillance Grid": upload_section()

if __name__ == "__main__":
    init_page_config()
    show_home()
