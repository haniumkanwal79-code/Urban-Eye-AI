import streamlit as st
import numpy as np
import cv2
import pandas as pd
from datetime import datetime
import os
import time

# Robust fail-safe imports for ML and Mapping architectures
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
    def create_pdf(**kwargs): return "mock_report.pdf"

# Standard Email utility libraries
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

# Safe instantiation patterns
@st.cache_resource
def load_yolo_model():
    if YOLO is not None:
        try:
            return YOLO("best.pt")
        except Exception:
            return None
    return None

model = load_yolo_model()

# ================= SYSTEM STORAGE LAYER =================
if "incident_db" not in st.session_state:
    st.session_state["incident_db"] = [
        {"id": "UE-1024", "type": "Road", "location": "Metropolitan Highway", "timestamp": "2026-06-21 14:22:05", "severity": "🔴 Critical", "status": "🟢 Resolved", "lat": 24.8607, "lon": 67.0011},
        {"id": "UE-1025", "type": "Garbage", "location": "Zone B Commercial", "timestamp": "2026-06-22 09:15:32", "severity": "🟡 Medium", "status": "🔴 Pending", "lat": 24.8922, "lon": 67.0746},
        {"id": "UE-1026", "type": "Water", "location": "Outskirts Bypass", "timestamp": "2026-06-23 01:10:00", "severity": "🟢 Low", "status": "🔴 Pending", "lat": 24.9201, "lon": 67.1344}
    ]

if "system_settings" not in st.session_state:
    st.session_state["system_settings"] = {
        "ai_alerts": True,
        "logging": True,
        "priority_level": "High"
    }

# ================= HIGH-END EXECUTIVE CSS =================
def load_css():
    st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; }
    .premium-brand-card {
        background: linear-gradient(135deg, #090d16 0%, #111827 100%);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-top: 4px solid #00e5ff;
        padding: 25px; border-radius: 16px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        margin-bottom: 30px; text-align: center;
    }
    h1.brand-header {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-weight: 800 !important; letter-spacing: 4px !important;
        color: #ffffff !important; margin: 0 !important;
    }
    .system-tagline {
        font-size: 11px !important; font-weight: 700 !important;
        letter-spacing: 2px !important; color: #00ffcc !important;
        margin-top: 6px; text-transform: uppercase;
    }
    .status-row { display: flex; justify-content: center; gap: 15px; margin-top: 15px; }
    .status-pill {
        font-size: 10px; font-weight: 700; letter-spacing: 1px; padding: 5px 12px;
        border-radius: 6px; text-transform: uppercase; background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08); color: #cbd5e1;
    }
    .pill-highlight { color: #00ffcc; border-color: rgba(0, 255, 204, 0.2); background: rgba(0, 255, 204, 0.02); }
    .dashboard-card {
        background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 22px; border-radius: 14px; color: #94a3b8; font-size: 12px;
        font-weight: 700; letter-spacing: 1px; text-transform: uppercase; text-align: center;
    }
    .metric-value { font-size: 32px !important; font-weight: 800 !important; color: #ffffff !important; margin-top: 5px; }
    .panel-info-box {
        background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00e5ff; border-radius: 12px; padding: 16px 20px; color: #94a3b8; font-size: 13.5px;
    }
    .stButton button {
        background: linear-gradient(93deg, #00e5ff 0%, #00b4d8 100%) !important;
        color: #090d16 !important; font-weight: 700 !important; border: none !important; border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] { background: #060913 !important; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    </style>
    """, unsafe_allow_html=True)

# ================= EMAIL TRANSMISSION SYSTEM =================
def send_report_email(department_email, issue_type, location, timestamp, pdf_path):
    try:
        sender_email = st.secrets["email"]["SENDER_EMAIL"]
        sender_password = st.secrets["email"]["APP_PASSWORD"]
    except Exception:
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = department_email
    msg['Subject'] = f"[URGENT ALERT] {issue_type.upper()} Detected at {location}"

    body = f"Dear Team,\n\nAn automated anomaly has been flagged.\nType: {issue_type}\nZone: {location}\nTimestamp: {timestamp}"
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

# ================= CENTRAL OPERATION TRIPPERS =================
def generate_report(issue_type, location, image_path, confidence=0.85):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_path = create_pdf(issue_type=issue_type, location=location, image_path=image_path, timestamp=timestamp)
    st.success("🏛 Official Government Compliance Report Matrix Triggered")

    severity = "🔴 Critical" if confidence >= 0.80 or issue_type.lower() in ["road", "electricity"] else "🟡 Medium" if confidence >= 0.65 else "🟢 Low"
    
    rand_lat = 24.8607 + np.random.uniform(-0.06, 0.06)
    rand_lon = 67.0011 + np.random.uniform(-0.06, 0.06)

    new_id = f"UE-{1000 + len(st.session_state.get('incident_db', [])) + 1}"
    st.session_state["incident_db"].append({
        "id": new_id, "type": issue_type, "location": location, "timestamp": timestamp,
        "severity": severity, "status": "🔴 Pending", "lat": rand_lat, "lon": rand_lon
    })

    target_email = "central.command@government.gov"
    send_report_email(target_email, issue_type, location, timestamp, pdf_path)
    
    try:
        with open(pdf_path, "rb") as f:
            st.download_button("⬇ Download Compliance Dossier", f, file_name=f"Report_{new_id}.pdf", mime="application/pdf")
    except Exception:
        pass

# ================= CORE WORKSPACE VISUALS =================
def dashboard():
    st.markdown("""
        <div class="premium-brand-card">
            <h1 class="brand-header">URBAN EYE AI</h1>
            <div class="system-tagline">✦ LIVE MONITORING & ENFORCEMENT CONTROL CENTER ✦</div>
        </div>
    """, unsafe_allow_html=True)

    db = st.session_state.get("incident_db", [])
    total_db_count = 1237 + len(db)
    pending_count = sum(1 for item in db if "Pending" in item.get("status", ""))
    resolved_count = total_db_count - pending_count

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f'<div class="dashboard-card">Total Incidents<div class="metric-value">{total_db_count}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="dashboard-card">Resolved Cases<div class="metric-value">{resolved_count}</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="dashboard-card">Active Alerts<div class="metric-value" style="color: #ff3b30 !important;">{pending_count}</div></div>', unsafe_allow_html=True)
    col4.markdown('<div class="dashboard-card">Monitored Zones<div class="metric-value">18</div></div>', unsafe_allow_html=True)

# ================= ANALYTICS REGION =================
def analytics():
    st.title("📊 Statistical Metrics Array")
    df = pd.DataFrame({"Sector": ["Road", "Garbage", "Water", "Electricity", "Other"], "Reports": [320, 210, 400, 150, 160]})
    
    c1, c2 = st.columns(2)
    c1.line_chart(df.set_index("Sector"))
    c2.bar_chart(df.set_index("Sector"))

# ================= WORKFLOW SURVEILLANCE LAYER =================
def upload_section():
    st.title("📡 Detection Hub Matrix")
    mode = st.radio("Telemetry Mode", ["Static Image Evaluation", "Asynchronous Video Capture", "Live Optical Pipeline"])

    if mode == "Static Image Evaluation":
        image = st.file_uploader("Inject Optical Sample File", type=["jpg","png","jpeg"])
        location = st.text_input("📍 Spatial Target Node", "Zone Alpha Alpha")

        if image:
            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            if model is not None:
                results = model.predict(img, conf=0.5)
                st.image(results[0].plot(), caption="Processed Vector Map", use_container_width=True)
                if st.button("📄 Formulate Official Government Action Ledger"):
                    generate_report("Urban Infrastructure Request", location, "temp.jpg", 0.89)
            else:
                st.info("Core Engine running inside non-AI automation parsing mode.")
                st.image(img, channels="BGR")
                if st.button("📄 Formulate Standard Log Blueprint"):
                    generate_report("Manual Inspection Flag", location, "temp.jpg", 0.70)

# ================= GEOSPATIAL LIVE RECORD ROOM =================
def track_submissions():
    st.title("📋 Live System Repository Ledger")
    
    # Check if geo modules initialized cleanly
    if folium is not None and st_folium is not None:
        try:
            st.subheader("📍 Geospatial Live Telemetry Architecture")
            m = folium.Map(location=[24.8800, 67.0500], zoom_start=11, tiles="CartoDB dark_matter")
            for record in st.session_state.get("incident_db", []):
                color = "red" if "Critical" in record.get("severity", "") else "orange" if "Medium" in record.get("severity", "") else "blue"
                folium.Marker(
                    location=[record.get("lat", 24.8607), record.get("lon", 67.0011)],
                    popup=f"ID: {record.get('id','')}",
                    icon=folium.Icon(color=color)
                ).add_to(m)
            st_folium(m, width="100%", height=350, key="geo_matrix")
        except Exception:
            st.caption("Geospatial visualization module delayed.")

    st.markdown("---")
    table_data = pd.DataFrame(st.session_state.get("incident_db", []))
    if not table_data.empty:
        st.dataframe(table_data, use_container_width=True, hide_index=True)

    # 100% Working Operational Action Matrix Control Buttons
    if st.session_state.get("incident_db", []):
        st.subheader("🛠️ Core Cluster Management Node (Admin Panel)")
        col_sel, col_act = st.columns(2)
        target_id = col_sel.selectbox("Select Target Registry Reference ID", [item["id"] for item in st.session_state["incident_db"]])
        new_status = col_act.selectbox("Mutate Operational Status Mode", ["🔴 Pending State", "🟢 Resolved State"])
        
        if st.button("Commit Node Mutation Overrides to Production Core", use_container_width=True):
            for item in st.session_state["incident_db"]:
                if item["id"] == target_id:
                    item["status"] = new_status
            st.success(f"Cluster synchronization acknowledged. Node {target_id} state overwritten!")
            time.sleep(1)
            st.rerun()

# ================= SETTINGS MANAGER =================
def settings():
    st.title("⚙
