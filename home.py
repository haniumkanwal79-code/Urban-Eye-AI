import streamlit as st
from ultralytics import YOLO
import numpy as np
import cv2
import pandas as pd
from datetime import datetime
from pdf_utils import create_pdf
import os
import time
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# Email libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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

# Cache model to avoid reloading on every rerun
@st.cache_resource
def load_yolo_model():
    return YOLO("best.pt")

model = load_yolo_model()

# ================= DYNAMIC DATABASE INITIALIZATION =================
# Initializing mockup persistent database state so no historical data is deleted
if "incident_db" not in st.session_state:
    st.session_state.incident_db = [
        {"id": "UE-1024", "type": "Road", "location": "Metropolitan Highway", "timestamp": "2026-06-21 14:22:05", "status": "🟢 Resolved"},
        {"id": "UE-1025", "type": "Garbage", "location": "Zone B Commercial", "timestamp": "2026-06-22 09:15:32", "status": "🔴 Pending"},
        {"id": "UE-1026", "type": "Water", "location": "Outskirts Bypass", "timestamp": "2026-06-23 01:10:00", "status": "🔴 Pending"}
    ]

# ================= HIGH-END EXECUTIVE CSS =================
def load_css():
    st.markdown("""
    <style>
    /* Global Container Adjustments */
    .block-container {
        padding-top: 2rem !important;
    }
    
    /* Sleek Premium Brand Top Card */
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
    
    h1.brand-header {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-weight: 800 !important;
        letter-spacing: 4px !important;
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

    /* Minimalist Status Pills */
    .status-row {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-top: 15px;
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

    /* Clean Colored Grid Cards */
    .dashboard-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 22px;
        border-radius: 14px;
        color: #94a3b8;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        text-align: center;
        transition: all 0.3s ease;
    }
    .dashboard-card:hover {
        border-color: rgba(0, 229, 255, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0, 229, 255, 0.08);
    }
    .metric-value {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin-top: 5px;
        letter-spacing: -0.5px;
    }
    
    /* Clean Notification Box */
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

    /* Custom Input Fields */
    div[data-testid="stWidgetLabel"] p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    .stTextInput input {
        background-color: #090d16 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    .stTextInput input:focus {
        border-color: #00e5ff !important;
    }
    
    /* Modern Gradient Action Buttons */
    .stButton button {
        background: linear-gradient(93deg, #00e5ff 0%, #00b4d8 100%) !important;
        color: #090d16 !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px !important;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(93deg, #00ffcc 0%, #00e5ff 100%) !important;
        transform: translateY(-0.5px);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #060913 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)


# ================= EMAIL SYSTEM =================
def send_report_email(department_email, issue_type, location, timestamp, pdf_path):
    try:
        sender_email = st.secrets["email"]["SENDER_EMAIL"]
        sender_password = st.secrets["email"]["APP_PASSWORD"]
    except Exception:
        st.error("🔑 Email credentials missing in Streamlit Secrets!")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = department_email
    msg['Subject'] = f"[URGENT ALERT] {issue_type.upper()} Detected at {location}"

    body = f"""Dear Department Team,

An urban issue has been automatically detected and flagged by the National Urban Intelligence System.

----------------------------------------------
INCIDENT LOG DETAILS
----------------------------------------------
Issue Detected : {issue_type}
Location Zone  : {location}
Timestamp      : {timestamp}
----------------------------------------------

The official government compliance report has been generated and is attached to this email. Please take immediate action.

This is an automated system generation alert. Please do not reply to this address.
"""
    msg.attach(MIMEText(body, 'plain'))

    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(pdf_path)}",
            )
            msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, department_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to transmit automated email notification: {str(e)}")
        return False


# ================= REPORT SYSTEM =================
def generate_report(issue_type, location, image_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_path = create_pdf(
        issue_type=issue_type,
        location=location,
        image_path=image_path,
        timestamp=timestamp
    )
    st.success("🏛 Official Government Report Generated")

    # Automatically save incident log inside runtime session state
    new_id = f"UE-{1000 + len(st.session_state.incident_db) + 1}"
    st.session_state.incident_db.append({
        "id": new_id,
        "type": issue_type,
        "location": location,
        "timestamp": timestamp,
        "status": "🔴 Pending"
    })

    department_directory = {
        "road": "road.maintenance@government.gov",
        "garbage": "waste.management@government.gov",
        "water": "water.sanitation@government.gov",
        "electricity": "power.grid@government.gov"
    }
    
    matched_issue = issue_type.lower().strip()
    target_email = department_directory.get(matched_issue, "central.command@government.gov")
    
    st.info(f"📬 Dispatching report to department endpoint: {target_email}...")
    email_status = send_report_email(target_email, issue_type, location, timestamp, pdf_path)
    
    if email_status:
        st.success("🚀 Report successfully routed and emailed to the department! ✅")

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇ Download Official Report (Gov Format)",
            f,
            file_name="National_Urban_Report.pdf",
            mime="application/pdf"
        )


# ================= DASHBOARD =================
def dashboard():
    st.markdown("""
        <div class="premium-brand-card">
            <h1 class="brand-header">URBAN EYE AI</h1>
            <div class="system-tagline">✦ LIVE MONITORING & ENFORCEMENT CENTER ✦</div>
            <div class="status-row">
                <span class="status-pill pill-highlight">● SMART CITY ENGINE: ACTIVE</span>
                <span class="status-pill">AI ENFORCEMENT</span>
                <span class="status-pill">VERSION 2.4</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Dynamic counts driven by live dataset matrix
    total_db_count = 1237 + len(st.session_state.incident_db)
    pending_count = sum(1 for item in st.session_state.incident_db if "Pending" in item["status"])
    resolved_count = total_db_count - pending_count

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="dashboard-card">Total Incidents<div class="metric-value">{total_db_count:,}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="dashboard-card">Resolved Cases<div class="metric-value">{resolved_count:,}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f
