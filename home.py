import os
import time
import cv2
import numpy as np
import pandas as pd
import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from datetime import datetime

# Email libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Gemini SDK
from google import genai

@st.cache_resource
def load_yolo_model():
    return YOLO("best.pt")

model = load_yolo_model()

# ================= CSS & UI =================
def load_css():
    st.markdown("""
    <style>
    .premium-brand-card { background: linear-gradient(135deg, #090d16 0%, #111827 100%); border-top: 4px solid #00e5ff; padding: 25px; border-radius: 16px; text-align: center; }
    .metric-value { font-size: 32px !important; font-weight: 800 !important; color: #ffffff !important; }
    .dashboard-card { background: rgba(15, 23, 42, 0.6); padding: 22px; border-radius: 14px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.06); }
    </style>
    """, unsafe_allow_html=True)

# ================= LOGIC FUNCTIONS =================
def generate_ai_action_plan(issue_type, location):
    try:
        api_key = st.secrets["gemini"]["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        prompt = f"Issue: {issue_type} at {location}. Provide a 3-bullet-point action plan."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except:
        return "Standard dispatch for " + issue_type

def generate_report(issue_type, location, image_path):
    from pdf_utils import create_pdf
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ai_plan = generate_ai_action_plan(issue_type, location)
    pdf_path = create_pdf(issue_type, location, image_path, timestamp)
    
    if "incident_db" not in st.session_state:
        st.session_state.incident_db = []
    
    st.session_state.incident_db.append({
        "id": f"UE-{1000 + len(st.session_state.incident_db)}",
        "type": issue_type,
        "location": location,
        "status": "🔴 Pending"
    })
    st.success(f"Report Generated: {issue_type}")

# ================= CAMERA TRANSFORMER =================
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

# ================= MAIN UI =================
def show_home():
    load_css()
    if "incident_db" not in st.session_state:
        st.session_state.incident_db = []
    if "frozen_frame" not in st.session_state:
        st.session_state.frozen_frame = None

    menu = st.sidebar.radio("🏛 CONTROL CENTER", ["🏛 Dashboard", "📡 Surveillance Grid"])

    if menu == "🏛 Dashboard":
        st.markdown('<div class="premium-brand-card"><h1>URBAN EYE AI</h1></div>', unsafe_allow_html=True)
        st.write("Welcome to Command Center.")

    elif menu == "📡 Surveillance Grid":
        st.title("Live Surveillance")
        
        # WEBRTC CAMERA
        ctx = webrtc_streamer(
            key="gov-live",
            video_transformer_factory=GovCamera,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )
        
        # FIX: Check ctx in session state
        st.session_state.ctx = ctx

        if st.button("⏸️ FREEZE CURRENT DETECTION"):
            if st.session_state.ctx and st.session_state.ctx.state.playing:
                if "current_active_frame" in st.session_state:
                    st.session_state.frozen_frame = st.session_state.current_active_frame.copy()
                    st.toast("Frame Locked!")
            else:
                st.error("Camera is not active. Click Start first.")

        if st.session_state.frozen_frame is not None:
            st.image(cv2.cvtColor(st.session_state.frozen_frame, cv2.COLOR_BGR2RGB))
            if st.button("Generate Report for Frozen Frame"):
                frozen_path = f"freeze_{int(time.time())}.jpg"
                cv2.imwrite(frozen_path, st.session_state.frozen_frame)
                generate_report("Detected Hazard", "Live Location", frozen_path)
