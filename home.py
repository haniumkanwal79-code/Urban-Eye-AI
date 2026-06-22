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

# Cache model to avoid reloading on every rerun
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


# ================= AI GENERATION SYSTEM (GEMINI LLM) =================
def generate_ai_action_plan(issue_type, location):
    try:
        api_key = st.secrets["gemini"]["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        prompt = f"You are an expert AI Smart City System. An urban municipal hazard has been detected.\nIssue Type: {issue_type}\nLocation Target: {location}\nProvide a concise 3-bullet-point operational action plan for dispatch field workers. Keep it highly professional, specific to the issue, and under 60 words total."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except Exception:
        return f"Standard deployment of {issue_type} emergency relief unit. Cordon off the area at {location} and inspect structural parameters safely."


# ================= EMAIL SYSTEM =================
def send_report_email(department_email, issue_type, location, timestamp, pdf_path, ai_plan):
    try:
        sender_email = st.secrets["email"]["SENDER_EMAIL"]
        sender_password = st.secrets["email"]["APP_PASSWORD"]
    except Exception:
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = department_email
    msg['Subject'] = f"[URGENT ALERT] {issue_type.upper()} Detected at {location}"
    body = f"Dear Department Team,\n\nAn urban issue has been detected.\n\nIssue: {issue_type}\nLocation: {location}\nTimestamp: {timestamp}\n\nAI Action Plan:\n{ai_plan}"
    msg.attach(MIMEText(body, 'plain'))

    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(pdf_path)}")
            msg.attach(part)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, department_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False


# ================= REPORT SYSTEM =================
def generate_report(issue_type, location, image_path):
    from pdf_utils import create_pdf
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with st.spinner("🤖 AI Brain Matrix is drafting targeted field action strategies..."):
        ai_plan = generate_ai_action_plan(issue_type, location)
    
    st.markdown(f'<div class="panel-info-box"><strong>🤖 AI ACTION PLAN:</strong><br>{ai_plan}</div>', unsafe_allow_html=True)
    pdf_path = create_pdf(issue_type=issue_type, location=location, image_path=image_path, timestamp=timestamp)
    
    if "incident_db" not in st.session_state: st.session_state.incident_db = []
    new_id = f"UE-{1000 + len(st.session_state.incident_db) + 1}"
    st.session_state.incident_db.append({"id": new_id, "type": issue_type, "location": location, "timestamp": timestamp, "status": "🔴 Pending", "action_plan": ai_plan})
    
    email_status = send_report_email("central.command@government.gov", issue_type, location, timestamp, pdf_path, ai_plan)
    if email_status:
        st.success(f"🚀 Report successfully routed! ✅")

    with open(pdf_path, "rb") as f:
        st.download_button(f"⬇ Download Report ({issue_type})", f, file_name=f"Report_{issue_type}.pdf", mime="application/pdf")


# ================= DASHBOARD =================
def dashboard():
    st.markdown('<div class="premium-brand-card"><h1 class="brand-header">URBAN EYE AI</h1></div>', unsafe_allow_html=True)
    total_db_count = 1237 + len(st.session_state.incident_db)
    pending_count = sum(1 for item in st.session_state.incident_db if "Pending" in item["status"])
    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="dashboard-card">Total Incidents<div class="metric-value">{total_db_count}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="dashboard-card">Pending<div class="metric-value" style="color: #ff3b30 !important;">{pending_count}</div></div>', unsafe_allow_html=True)
    col3.markdown('<div class="dashboard-card">Zones<div class="metric-value">18</div></div>', unsafe_allow_html=True)


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
            st.image(results[0].plot(), use_container_width=True)
            if st.button("Generate Report"):
                path = f"tmp_{time.time()}.jpg"
                cv2.imwrite(path, img)
                generate_report("General Issue", location, path)

    elif mode == "Live Camera":
        st.warning("🔴 LIVE SURVEILLANCE ACTIVE")
        location = st.text_input("📍 Location Tag", "Live Active Zone")

        if "frozen_frame" not in st.session_state: st.session_state.frozen_frame = None
        if "frozen_issues" not in st.session_state: st.session_state.frozen_issues = []

        class GovCamera(VideoTransformerBase):
            def transform(self, frame):
                img = frame.to_ndarray(format="bgr24")
                if model:
                    results = model.predict(img, conf=0.5, verbose=False)
                    detected = []
                    for r in results:
                        for box in r.boxes:
                            cls = int(box.cls[0])
                            name = model.names[cls]
                            if name.lower() != "person":
                                detected.append(name)
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    st.session_state.current_active_frame = img.copy()
                    st.session_state.current_active_issues = list(set(detected))
                return img

        ctx = webrtc_streamer(
            key="gov-live",
            video_transformer_factory=GovCamera,
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⏸️ FREEZE CURRENT DETECTION"):
                if ctx.state.playing and "current_active_frame" in st.session_state:
                    st.session_state.frozen_frame = st.session_state.current_active_frame.copy()
                    st.session_state.frozen_issues = st.session_state.current_active_issues
                    st.rerun()
                else:
                    st.error("Camera inactive.")
        with col_btn2:
            if st.button("🔄 CLEAR"):
                st.session_state.frozen_frame = None
                st.rerun()

        if st.session_state.frozen_frame is not None:
            st.image(cv2.cvtColor(st.session_state.frozen_frame, cv2.COLOR_BGR2RGB), use_container_width=True)
            if st.button("📄 TRANSMIT REPORT"):
                path = f"live_{int(time.time())}.jpg"
                cv2.imwrite(path, st.session_state.frozen_frame)
                for issue in st.session_state.frozen_issues:
                    generate_report(issue, location, path)

# ================= MAIN RUN FUNCTION =================
def show_home():
    if "incident_db" not in st.session_state: st.session_state.incident_db = []
    load_css()
    menu = st.sidebar.radio("🏛 CONTROL CENTER", ["🏛 Dashboard", "📡 Surveillance Grid", "📊 Analytics", "📋 Track Submissions", "⚙️ Settings"])
    
    if menu == "🏛 Dashboard": dashboard()
    elif menu == "📡 Surveillance Grid": upload_section()
    else: st.write("Tab content...")

if __name__ == "__main__":
    init_page_config()
    show_home()
