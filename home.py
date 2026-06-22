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

try:
    model = load_yolo_model()
except Exception:
    model = None

# ================= DYNAMIC DATABASE INITIALIZATION =================
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
    .block-container {
        padding-top: 2rem !important;
    }
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
    .stButton button {
        background: linear-gradient(93deg, #00e5ff 0%, #00b4d8 100%) !important;
        color: #090d16 !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }
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
            <div class="system-tagline">✦ LIVE MONITORING & ENFORCEMENT center ✦</div>
            <div class="status-row">
                <span class="status-pill pill-highlight">● SMART CITY ENGINE: ACTIVE</span>
                <span class="status-pill">AI ENFORCEMENT</span>
                <span class="status-pill">VERSION 2.4</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    total_db_count = 1237 + len(st.session_state.incident_db)
    pending_count = sum(1 for item in st.session_state.incident_db if "Pending" in item["status"])
    resolved_count = total_db_count - pending_count

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="dashboard-card">Total Incidents<div class="metric-value">{total_db_count}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="dashboard-card">Resolved Cases<div class="metric-value">{resolved_count}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="dashboard-card">Active Alerts<div class="metric-value" style="color: #ff3b30 !important;">{pending_count}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="dashboard-card">Monitored Zones<div class="metric-value">18</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="panel-info-box">
        <strong>💡 AI INSIGHT ENGINE:</strong><br>
        High violation activity detected in metropolitan highway zones during late evening hours (6 PM - 11 PM).
    </div>
    """, unsafe_allow_html=True)


# ================= DETECTION =================
def upload_section():
    st.title("📡 AI Surveillance & Detection Grid")
    mode = st.radio("Select Mode", ["Image", "Video", "Live Camera"])

    if mode == "Image":
        image = st.file_uploader("Upload City Evidence Image", type=["jpg","png","jpeg"])
        location = st.text_input("📍 Location Tag", "Unknown Zone")

        if image:
            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            if model:
                results = model.predict(img, conf=0.5)
                annotated = results[0].plot()
                st.image(annotated, caption="AI Detection Output", use_container_width=True)

                detected = []
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        name = model.names[cls]
                        if name.lower() != "person":
                            detected.append(name)

                detected = list(set(detected))
                st.success("Detection Completed ✔")
                st.write(detected)

                if st.button("📄 Generate Government Report"):
                    img_path = f"gov_report_{datetime.now().timestamp()}.jpg"
                    cv2.imwrite(img_path, img)
                    for issue in detected:
                        generate_report(issue, location, img_path)
            else:
                st.error("AI Model File ('best.pt') missing or failed to initialize.")

    elif mode == "Video":
        st.info("📡 Video Intelligence Mode Active")
        video_file = st.file_uploader("Upload Video", type=["mp4","avi","mov"])

        if video_file and model:
            temp_path = "temp_video.mp4"
            with open(temp_path, "wb") as f:
                f.write(video_file.read())

            cap = cv2.VideoCapture(temp_path)
            detected_all = []
            stframe = st.empty()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = model.predict(frame, conf=0.5)
                annotated = results[0].plot()
                stframe.image(annotated, channels="BGR")

                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        name = model.names[cls]
                        if name.lower() != "person":
                            detected_all.append(name)

            cap.release()
            detected_all = list(set(detected_all))
            st.success(f"Analysis Completed ✔ | Issues: {detected_all}")

    elif mode == "Live Camera":
        st.warning("🔴 LIVE SURVEILLANCE ACTIVE")
        location = st.text_input("📍 Location Tag", "Unknown Zone")

        if "last_frame" not in st.session_state:
            st.session_state.last_frame = None
        if "last_detected" not in st.session_state:
            st.session_state.last_detected = []

        class GovCamera(VideoTransformerBase):
            def transform(self, frame):
                img = frame.to_ndarray(format="bgr24")
                if model:
                    results = model.predict(img, conf=0.5)
                    detected = []

                    for r in results:
                        for box in r.boxes:
                            cls = int(box.cls[0])
                            name = model.names[cls]
                            if name.lower() != "person":
                                detected.append(name)
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,255), 2)

                    if detected:
                        st.session_state.last_frame = img.copy()
                        st.session_state.last_detected = list(set(detected))
                return img

        webrtc_streamer(
            key="gov-live",
            video_transformer_factory=GovCamera,
            media_stream_constraints={"video": True, "audio": False}
        )

        if st.button("📸 CAPTURE & REPORT"):
            if st.session_state.last_frame is not None:
                img_path = f"live_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, st.session_state.last_frame)
                for issue in st.session_state.last_detected:
                    generate_report(issue, location, img_path)


# ================= ANALYTICS =================
def analytics():
    st.markdown("""
        <div class="premium-brand-card">
            <h1 class="brand-header">INTELLIGENCE ANALYTICS CENTER</h1>
            <div class="system-tagline">✦ DATA TRENDS & PREDICTIVE VIOLATION SYSTEM ✦</div>
            <div class="status-row">
                <span class="status-pill pill-highlight">ACCURACY: 78%</span>
                <span class="status-pill">REAL-TIME DATA</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    total_db_count = 1237 + len(st.session_state.incident_db)
    pending_count = sum(1 for item in st.session_state.incident_db if "Pending" in item["status"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="dashboard-card">Total Reports<div class="metric-value">{total_db_count}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="dashboard-card">Avg Accuracy<div class="metric-value">78%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="dashboard-card">Active Alerts<div class="metric-value" style="color: #ff3b30 !important;">{pending_count}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="dashboard-card">Monitored Zones<div class="metric-value">18</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    df = pd.DataFrame({
        "Sector": ["Road", "Garbage", "Water", "Electricity", "Other"],
        "Reports": [320, 210, 400, 150, 160]
    })

    colA, colB = st.columns(2)
    with colA:
        st.subheader("📈 Sector Wise Reports Trend")
        st.line_chart(df.set_index("Sector"))
        st.bar_chart(df.set_index("Sector"))

    with colB:
        st.subheader("🔥 Risk Heatmap Simulation")
        heat_df = pd.DataFrame({
            "Zone A": [8, 3, 5],
            "Zone B": [6, 9, 2],
            "Zone C": [4, 7, 6]
        }, index=["Road", "Garbage", "Water"])
        st.dataframe(heat_df, use_container_width=True)

    st.markdown("""
    <div class="panel-info-box">
        <strong>🧠 PREDICTIVE INSIGHT DETAILS:</strong><br><br>
        • High violation density detected in ROAD sector (Urban highways).<br>
        • Garbage complaints increasing in Zone B (Possible waste management failure).<br>
        • Water-related issues stable but rising in outskirts.<br>
        • Predictive Alert: Next 7 days → 12% increase in road violations expected.
    </div>
    """, unsafe_allow_html=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇ Download Intelligence Report (CSV)",
        data=csv,
        file_name="national_intelligence_report.csv",
        mime="text/csv"
    )

# ================= TRACK SUBMISSIONS & ACTION CENTER =================
def track_submissions():
    st.title("📋 Live Incident Tracking Room")
    st.markdown("""
    <div class="panel-info-box">
        <strong>LIVE TELEMETRY WORKSPACE:</strong><br>
        Monitor active complaints filed into the server architecture. Toggle individual status states below.
    </div>
    """, unsafe_allow_html=True)

    table_data = pd.DataFrame(st.session_state.incident_db)
    st.dataframe(table_data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("🛠️ Admin Action Center Control")
    
    col_sel, col_act = st.columns(2)
    with col_sel:
        target_id = st.selectbox("Select Incident ID to Update", [item["id"] for item in st.session_state.incident_db])
    with col_act:
        new_status = st.selectbox("Assign Action Status Flag", ["🔴 Pending", "🟢 Resolved"])
        
    if st.button("Commit Status Update to Cluster Matrix", use_container_width=True):
        for item in st.session_state.incident_db:
            if item["id"] == target_id:
                item["status"] = new_status
        st.success(f"System Record updated successfully: {target_id} is now set to {new_status}!")
        st.try_rerun() if hasattr(st, "try_rerun") else st.rerun()

# ================= SETTINGS =================
def settings():
    st.title("⚙️ Control Panel Settings")
    st.checkbox("Enable AI Alerts", value=True)
    st.checkbox("Enable Automated System Logging", value=True)
    st.selectbox("System Priority Level", ["Low", "Medium", "High", "Critical"])


# ================= MAIN RUN FUNCTION =================
def show_home():
    load_css()
    menu = st.sidebar.radio(
        "🏛 CONTROL CENTER",
        ["🏛 Dashboard", "📡 Surveillance Grid", "📊 Analytics", "📋 Track Submissions", "⚙️ Settings"]
    )

    st.sidebar.markdown("---")
    user_email = st.session_state.user.email if (hasattr(st.session_state, 'user') and st.session_state.user) else "Authorized User"
    st.sidebar.caption(f"Logged in as: {user_email}")
    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.user = None
        st.try_rerun() if hasattr(st, "try_rerun") else st.rerun()

    st.sidebar.success("SYSTEM ACTIVE")
    st.sidebar.info("YOLOv8 AI Engine Running")

    if menu == "🏛 Dashboard":
        dashboard()
    elif menu == "📡 Surveillance Grid":
        upload_section()
    elif menu == "📊 Analytics":
        analytics()
    elif menu == "📋 Track Submissions":
        track_submissions()
    elif menu == "⚙️ Settings":
        settings()

# Standalone testing backup
if __name__ == "__main__":
    init_page_config()
    show_home()
