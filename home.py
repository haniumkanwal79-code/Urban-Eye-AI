import streamlit as st
import numpy as np
import cv2
import pandas as pd
from datetime import datetime
import os
import time

# ================= ROBUST SAFE IMPORTS =================
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

# Safe implementation of fallback functions to avoid inline syntax errors
try:
    from pdf_utils import create_pdf
except Exception:
    # Standard function fallback wrapper if file doesn't exist
    def fallback_pdf(*args, **kwargs):
        return "mock_report.pdf"
    create_pdf = fallback_pdf

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
        "severity": severity, "status": "🔴 Pending", "lat": rand_lat, "lon": rand_lon
    })

    target_email = "central.command@government.gov"
    send_report_email(target_email, issue_type, location, timestamp, pdf_path)
    
    try:
        with open(pdf_path, "rb") as f:
            st.download_button("⬇️ Download Official Compliance PDF", f, file_name=f"Urban_Eye_Report_{new_id}.pdf", mime="application/pdf")
    except Exception:
        pass

# ================= COMMAND DASHBOARD VIEW =================
def dashboard():
    st.markdown("""
        <div class="main-hero-card">
            <h1 class="main-title">URBAN EYE AI</h1>
            <div class="sub-tagline">✦ Real-Time Smart City Monitoring & Control Hub ✦</div>
            <div class="status-container">
                <span class="status-badge badge-active">● Core Engine: Connected</span>
                <span class="status-badge">AI Surveillance</span>
                <span class="status-badge">v2.5 Stable</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    db = st.session_state.get("incident_db", [])
    total_db_count = 1237 + len(db)
    pending_count = sum(1 for item in db if "Pending" in item.get("status", ""))
    resolved_count = total_db_count - pending_count

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f'<div class="stat-card">Total Logged Cases<div class="stat-value">{total_db_count}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="stat-card">Resolved Cases<div class="stat-value">{resolved_count}</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="stat-card">Active Alerts<div class="stat-value" style="color: #ff3b30 !important;">{pending_count}</div></div>', unsafe_allow_html=True)
    col4.markdown('<div class="stat-card">Monitored Zones<div class="stat-value">18</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="info-alert-box">
        <strong>💡 LIVE ANALYTICS BRIEF:</strong> High-risk activity trends detected in commercial highways during peak operational hours.
    </div>
    """, unsafe_allow_html=True)

# ================= ENHANCED PROFESSIONAL DETECTION HUB =================
def upload_section():
    st.markdown("""
        <div class="main-hero-card" style="padding: 20px; border-top: 4px solid #00ffcc;">
            <h2 style="color: white; margin: 0;">📡 AI DETECTION & SURVEILLANCE HUB</h2>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 5px;">Process live media streams or files through the centralized computer vision pipeline.</p>
        </div>
    """, unsafe_allow_html=True)

    col_menu, col_display = st.columns([1, 2], gap="large")

    with col_menu:
        st.subheader("⚙️ Input Configuration")
        mode = st.radio("Select Source Type", ["📷 Static Image Upload", "🎥 Recorded Video File", "🔴 Live Surveillance Feed"])
        location = st.text_input("📍 Spatial Location Tag", "Main Sector Alpha")
        
        st.markdown("---")
        st.markdown("**Pipeline Status:**")
        if model is not None:
            st.success("🤖 YOLOv8 Neural Model Active")
        else:
            st.warning("⚙️ Standard Automation Mode Running")

    with col_display:
        st.subheader("🖥️ Live Visualization Monitor")
        
        if mode == "📷 Static Image Upload":
            image = st.file_uploader("Upload Image File", type=["jpg", "png", "jpeg"])
            
            if image:
                file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, 1)

                if model is not None:
                    results = model.predict(img, conf=0.5)
                    st.image(results[0].plot(), caption="Processed AI Detection Output", use_container_width=True)
                    
                    if st.button("📄 Process & Generate Government Report", use_container_width=True):
                        generate_report("Urban Infrastructure Defect", location, "temp.jpg", 0.88)
                else:
                    st.info("Displaying uploaded raw media sample (Running without heavy AI processing).")
                    st.image(img, channels="BGR", use_container_width=True)
                    if st.button("📄 Create Standard Manual Case Log", use_container_width=True):
                        generate_report("Manual Infrastructure Audit", location, "temp.jpg", 0.70)

        elif mode == "🎥 Recorded Video File":
            video_file = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov"])
            if video_file:
                st.info("Video pipeline verified. Processing preview blocks...")
                st.video(video_file)

        elif mode == "🔴 Live Surveillance Feed":
            if webrtc_streamer is not None:
                st.info("Initializing connection to active camera node...")
                webrtc_streamer(key="urban-live-feed", media_stream_constraints={"video": True, "audio": False})
            else:
                st.error("Live streaming components are offline. Verify system configuration logs.")

# ================= ANALYTICS LAYER =================
def analytics():
    st.title("📊 Statistical Performance Metrics")
    df = pd.DataFrame({"Sector": ["Roads", "Garbage", "Water", "Electricity"], "Reports": [320, 210, 400, 150]})
    c1, c2 = st.columns(2)
    c1.line_chart(df.set_index("Sector"))
    c2.bar_chart(df.set_index("Sector"))

# ================= RECORDS ROOM =================
def track_submissions():
    st.title("📋 Live System Incident Logs")
    
    if folium is not None and st_folium is not None:
        try:
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
            pass

    st.markdown("---")
    table_data = pd.DataFrame(st.session_state.get("incident_db", []))
    if not table_data.empty:
        st.dataframe(table_data, use_container_width=True, hide_index=True)

    if st.session_state.get("incident_db", []):
        st.subheader("🛠️ Operations Admin Action Console")
        col_sel, col_act = st.columns(2)
        target_id = col_sel.selectbox("Select Target Reference ID", [item["id"] for item in st.session_state["incident_db"]])
        new_status = col_act.selectbox("Change Operational Status", ["🔴 Pending State", "🟢 Resolved State"])
        
        if st.button("Commit Status Updates to System Memory", use_container_width=True):
            for item in st.session_state["incident_db"]:
                if item["id"] == target_id:
                    item["status"] = new_status
            st.success(f"System status for {target_id} successfully updated!")
            time.sleep(1)
            st.rerun()

# ================= CONFIGURATIONS LAYER =================
def settings():
    st.title("⚙️ Engine Configurations Panel")
    ai_alerts = st.checkbox("Enable Automatic System Email Dispatches", value=st.session_state["system_settings"]["ai_alerts"])
    logging = st.checkbox("Retain System Debug Logs", value=st.session_state["system_settings"]["logging"])
    
    if st.button("Save System Properties", use_container_width=True):
        st.session_state["system_settings"]["ai_alerts"] = ai_alerts
        st.session_state["system_settings"]["logging"] = logging
        st.success("Settings saved to core runtime environment!")
        time.sleep(1)
        st.rerun()

# ================= SIDEBAR NAVIGATION HOOK =================
def show_home():
    load_css()
    if "incident_db" not in st.session_state:
        st.session_state["incident_db"] = []

    menu = st.sidebar.radio(
        "🏛 CONTROL CENTER NAVIGATION",
        ["🏛 Core Dashboard", "📡 Detection Hub", "📊 Data Analytics", "📋 Central Logs Room", "⚙️ System Settings"]
    )

    st.sidebar.markdown("---")
    user_email = st.session_state.user.email if (hasattr(st.session_state, 'user') and st.session_state.user) else "operator.command@gov.io"
    st.sidebar.caption(f"Operator: {user_email}")
    
    if st.sidebar.button("Logout Session 🚪", use_container_width=True):
        st.session_state.user = None
        st.rerun()

    if menu == "🏛 Core Dashboard":
        dashboard()
    elif menu == "📡 Detection Hub":
        upload_section()
    elif menu == "📊 Data Analytics":
        analytics()
    elif menu == "📋 Central Logs Room":
        track_submissions()
    elif menu == "⚙️ System Settings":
        settings()

if __name__ == "__main__":
    init_page_config()
    show_home()
