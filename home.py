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

# Email sending ke liye zaroori libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ================= PAGE CONFIG =================
# Is function ko safely isolate kiya hai taake app.py ke sath duplicate page config ka error na aaye
def init_page_config():
    try:
        st.set_page_config(
            page_title="🏛 National Urban Intelligence System",
            page_icon="🏛",
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


# ================= PREMIUM CSS (UPGRADED UI ONLY) =================
def load_css():
    st.markdown("""
    <style>
    /* GLOBAL */
    body {
        background: radial-gradient(circle at top, #0b1220, #050814);
    }
    /* TITLE */
    .gov-title {
        font-size:52px;
        font-weight:900;
        text-align:center;
        color:#00e5ff;
        letter-spacing:3px;
        text-shadow:0px 0px 20px rgba(0,229,255,0.6);
        margin-bottom:5px;
    }
    .gov-subtitle {
        text-align:center;
        color:#a9c4d8;
        margin-bottom:30px;
        font-size:17px;
    }
    /* GLASS CARD */
    .gov-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        padding:24px;
        border-radius:18px;
        box-shadow:0px 0px 25px rgba(0,229,255,0.10);
        color:white;
        text-align:center;
        border:1px solid rgba(0,229,255,0.2);
        transition:0.3s ease-in-out;
    }
    .gov-card:hover {
        transform: scale(1.05);
        box-shadow:0px 0px 35px rgba(0,229,255,0.35);
    }
    /* METRICS */
    .metric-big {
        font-size:34px;
        font-weight:900;
        color:#00ffcc;
        text-shadow:0px 0px 10px rgba(0,255,204,0.4);
    }
    /* ALERT BOX */
    .alert-box {
        background: linear-gradient(90deg, #0f172a, #111c33);
        border-left:5px solid #00e5ff;
        padding:14px;
        border-radius:12px;
        color:white;
        box-shadow:0px 0px 20px rgba(0,229,255,0.15);
    }
    /* BUTTONS */
    .stButton button {
        background: linear-gradient(90deg, #00e5ff, #00ffcc);
        color:black;
        font-weight:bold;
        border-radius:10px;
        border:none;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow:0px 0px 15px rgba(0,255,204,0.5);
    }
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1220, #050814);
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
    st.markdown('<div class="gov-title">🏛 NATIONAL URBAN INTELLIGENCE CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="gov-subtitle">Real-Time Smart City Monitoring & AI Enforcement System</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="gov-card">🔥 TOTAL INCIDENTS<br><div class="metric-big">1240</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="gov-card">✅ RESOLVED CASES<br><div class="metric-big">980</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="gov-card">⚠ ACTIVE ALERTS<br><div class="metric-big">260</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="gov-card">📍 MONITORED ZONES<br><div class="metric-big">18</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="alert-box">
    🧠 AI INSIGHT: High violation density detected in metropolitan highway zones (6PM - 11PM).
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

    elif mode == "Video":
        st.info("📡 Video Intelligence Mode Active")
        video_file = st.file_uploader("Upload Video", type=["mp4","avi","mov"])

        if video_file:
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
    <style>
    .intel-header{ font-size:32px; font-weight:900; color:#00e5ff; text-align:center; margin-bottom:10px; }
    .intel-sub{ text-align:center; color:#9fb3c8; margin-bottom:25px; }
    .kpi-box{ background: linear-gradient(135deg,#0f172a,#111c33); padding:20px; border-radius:16px; text-align:center; border:1px solid rgba(0,229,255,0.2); box-shadow:0px 0px 20px rgba(0,229,255,0.08); }
    .kpi-value{ font-size:28px; font-weight:900; color:#00ffcc; }
    .kpi-label{ color:#9fb3c8; font-size:14px; }
    .intel-box{ background:#1b1f36; padding:15px; border-left:5px solid #00e5ff; border-radius:10px; color:white; margin-top:15px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="intel-header">📊 NATIONAL INTELLIGENCE ANALYTICS CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="intel-sub">Real-Time Urban Monitoring | Predictive Violation System | AI Insights Engine</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="kpi-box"><div class="kpi-value">1240</div><div class="kpi-label">Total Reports</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-box"><div class="kpi-value">78%</div><div class="kpi-label">Detection Accuracy</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-box"><div class="kpi-value">260</div><div class="kpi-label">Active Alerts</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="kpi-box"><div class="kpi-value">18</div><div class="kpi-label">Monitored Zones</div></div>', unsafe_allow_html=True)

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
    <div class="intel-box">
    🧠 AI INSIGHT ENGINE:<br><br>
    • High violation density detected in ROAD sector (Urban highways)<br>
    • Garbage complaints increasing in Zone B (Possible waste management failure)<br>
    • Water-related issues stable but rising in outskirts<br>
    • Predictive Alert: Next 7 days → 12% increase in road violations expected
    </div>
    """, unsafe_allow_html=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇ Download Intelligence Report (CSV)",
        data=csv,
        file_name="national_intelligence_report.csv",
        mime="text/csv"
    )

# ================= SETTINGS =================
def settings():
    st.title("⚙️ Control Panel")
    st.checkbox("Enable AI Alerts")
    st.checkbox("Enable Logging")
    st.selectbox("Priority Level", ["Low", "Medium", "High", "Critical"])


# ================= MAIN RUN FUNCTION =================
def show_home():
    load_css()
    menu = st.sidebar.radio(
        "🏛 CONTROL CENTER",
        ["🏛 Dashboard", "📡 Surveillance Grid", "📊 Analytics", "⚙️ Settings"]
    )

    st.sidebar.markdown("---")
    user_email = st.session_state.user.email if (hasattr(st.session_state, 'user') and st.session_state.user) else "Authorized User"
    st.sidebar.caption(f"Logged in as: {user_email}")
    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.user = None
        st.rerun()

    st.sidebar.success("SYSTEM ACTIVE")
    st.sidebar.info("YOLOv8 AI Engine Running")

    if menu == "🏛 Dashboard":
        dashboard()
    elif menu == "📡 Surveillance Grid":
        upload_section()
    elif menu == "📊 Analytics":
        analytics()
    elif menu == "⚙️ Settings":
        settings()

# Standalone testing backup
if __name__ == "__main__":
    init_page_config()
    show_home()
