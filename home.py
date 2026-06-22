import streamlit as st
import numpy as np
import cv2
import pandas as pd
from datetime import datetime
import os
import time

# ================= SAFE BACKEND INTEGRATIONS =================
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

try:
    from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
except Exception:
    VideoTransformerBase = object
    webrtc_streamer = None

try:
    import folium
    from streamlit_folium import st_folium
except Exception:
    folium = None
    st_folium = None

try:
    from pdf_utils import create_pdf
except Exception:
    def create_pdf(**kwargs):
        return "mock_report.pdf"

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ================= PAGE INITIALIZATION =================
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
    if YOLO is not None:
        try:
            return YOLO("best.pt")
        except Exception:
            return None
    return None

model = load_yolo_model()

# ================= CENTRAL DATA PLATFORM =================
if "incident_db" not in st.session_state:
    st.session_state["incident_db"] = [
        {"id": "UE-1024", "type": "Road Defect", "location": "Metropolitan Highway", "timestamp": "2026-06-21 14:22:05", "severity": "🔴 Critical", "status": "🟢 Resolved", "lat": 24.8607, "lon": 67.0011},
        {"id": "UE-1025", "type": "Garbage Accumulation", "location": "Zone B Commercial", "timestamp": "2026-06-22 09:15:32", "severity": "🟡 Medium", "status": "🔴 Pending", "lat": 24.8922, "lon": 67.0746},
        {"id": "UE-1026", "type": "Water Leakage", "location": "Outskirts Bypass", "timestamp": "2026-06-23 01:10:00", "severity": "🟢 Low", "status": "🔴 Pending", "lat": 24.9201, "lon": 67.1344}
    ]

if "system_settings" not in st.session_state:
    st.session_state["system_settings"] = {
        "ai_alerts": True,
        "logging": True,
        "priority_level": "High"
    }

# ================= MODERN ENTERPRISE UI STYLING =================
def load_css():
    st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; }
    .main-hero-card {
        background: linear-gradient(135deg, #070a12 0%, #101726 100%);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-top: 4px solid #00e5ff;
        padding: 30px; border-radius: 16px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        margin-bottom: 25px; text-align: center;
    }
    h1.main-title {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-weight: 800 !important; letter-spacing: 3px !important;
        color: #ffffff !important; margin: 0 !important;
    }
    .sub-tagline {
        font-size: 12px !important; font-weight: 600 !important;
        letter-spacing: 2px !important; color: #00ffcc !important;
        margin-top: 8px; text-transform: uppercase;
    }
    .status-container { display: flex; justify-content: center; gap: 12px; margin-top: 15px; }
    .status-badge {
        font-size: 11px; font-weight: 700; padding: 6px 14px;
        border-radius: 6px; text-transform: uppercase; background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1); color: #e2e8f0;
    }
    .badge-active { color: #00ffcc; border-color: rgba(0, 255, 204, 0.3); background: rgba(0, 255, 204, 0.03); }
    .stat-card {
        background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px; border-radius: 12px; text-align: center; color: #94a3b8;
        font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
    }
    .stat-value { font-size: 34px !important; font-weight: 800 !important; color: #ffffff !important; margin-top: 5px; }
    .info-alert-box {
        background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00e5ff; border-radius: 10px; padding: 15px 20px; color: #cbd5e1; font-size: 14px;
    }
    .stButton button {
        background: linear-gradient(90deg, #00e5ff 0%, #00b4d8 100%) !important;
        color: #090d16 !important; font-weight: 700 !important; border: none !important;
        border-radius: 8px !important; padding: 10px 20px !important; transition: all 0.3s;
    }
    .stButton button:hover { transform: translateY(-1px); box-shadow: 0 5px 15px rgba(0, 229, 255, 0.4); }
    section[data-testid="stSidebar"] { background: #05070f !important; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    </style>
    """, unsafe_allow_html=True)

# ================= AUTOMATED SECURITY DISPATCH SYSTEM =================
def send_report_email(department_email, issue_type, location, timestamp, pdf_path):
    try:
        sender_email = st.secrets["email"]["SENDER_EMAIL"]
        sender_password = st.secrets["email"]["APP_PASSWORD"]
    except Exception:
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = department_email
    msg['Subject'] = f"[URGENT ALERT] {issue_type.upper()} Reported at {location}"

    body = f"Hello Team,\n\nAn urban issue has been automatically logged by the AI System.\n\nDetails:\n- Issue: {issue_type}\n- Location: {location}\n- Time: {timestamp}\n\nPlease check the attached PDF report."
    msg.attach(MIMEText(body, 'plain'))

    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(pdf_path)}")
                msg.attach(part)
        except Exception:
            pass

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, department_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

# ================= CORE LOGIC SYSTEM =================
def generate_report(issue_type, location, image_path, confidence=0.85):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_path = create_pdf(issue_type=issue_type, location=location, image_path=image_path, timestamp=timestamp)
    st.success("📝 Official Government Compliance Report Generated Successfully!")

    severity = "🔴 Critical" if confidence >= 0.80 or issue_type.lower() in ["road defect", "electricity barrier"] else "🟡 Medium" if confidence >= 0.65 else "🟢 Low"
    
    rand_lat = 24.8607 + np.random.uniform(-0.05, 0.05)
    rand_lon = 67.0011 + np.random.uniform(-0.05, 0.05)

    new_id = f"UE-{1000 + len(st.session_state.get('incident_db', [])) + 1}"
    st.session_state["incident_db"].append({
        "id": new_id, "type": issue_type, "location": location, "timestamp": timestamp,
        "severity": severity
