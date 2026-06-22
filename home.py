import os
import time
import smtplib
from datetime import datetime
import cv2
import numpy as np
import pandas as pd
import streamlit as st
import threading # 1. Added for Thread Safety
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

# ================= SAFEGUARD LOCK =================
frame_lock = threading.Lock()

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

# ... (CSS function wahi rahega jo aapka tha) ...
def load_css():
    st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; }
    .premium-brand-card { background: linear-gradient(135deg, #090d16 0%, #111827 100%); border: 1px solid rgba(0, 229, 255, 0.2); border-top: 4px solid #00e5ff; padding: 25px; border-radius: 16px; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5); margin-bottom: 30px; text-align: center; }
    h1.brand-header { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: 800 !important; letter-spacing: 4px !important; color: #ffffff !important; margin: 0 !important; }
    .system-tagline { font-size: 11px !important; font-weight: 700 !important; letter-spacing: 2px !important; color: #00ffcc !important; margin-top: 6px; text-transform: uppercase; }
    .status-row { display: flex; justify-content: center; gap: 15px; margin-top: 15px; }
    .status-pill { font-size: 10px; font-weight: 700; letter-spacing: 1px; padding: 5px 12px; border-radius: 6px; text-transform: uppercase; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); color: #cbd5e1; }
    .pill-highlight { color: #00ffcc; border-color: rgba(0, 255, 204, 0.2); background: rgba(0, 255, 204, 0.02); }
    .dashboard-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.06); padding: 22px; border-radius: 14px; color: #94a3b8; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; text-align: center; }
    .metric-value { font-size: 32px !important; font-weight: 800 !important; color: #ffffff !important; margin-top: 5px; letter-spacing: -0.5px; }
    .panel-info-box { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #00e5ff; border-radius: 12px; padding: 16px 20px; color: #94a3b8; font-size: 13.5px; line-height: 1.6; margin-bottom: 25px; }
    .panel-info-box strong { color: #ffffff; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# ... (generate_ai_action_plan, send_report_email, generate_report functions same rahegi) ...

# ================= DETECTION (UPDATED) =================
def upload_section():
    st.title("📡 AI Surveillance & Detection Grid")
    mode = st.radio("Select Mode", ["Image", "Video", "Live Camera"])

    if mode == "Live Camera":
        st.warning("🔴 LIVE SURVEILLANCE ACTIVE")
        location = st.text_input("📍 Location Tag", "Live Active Zone")

        # Session State for camera
        if "camera_active" not in st.session_state: st.session_state.camera_active = False

        class GovCamera(VideoTransformerBase):
            def transform(self, frame):
                img = frame.to_ndarray(format="bgr24")
                st.session_state.camera_active = True
                if model:
                    results = model.predict(img, conf=0.5, verbose=False)
                    detected = []
                    for r in results:
                        for box in r.boxes:
                            name = model.names[int(box.cls[0])]
                            if name.lower() != "person":
                                detected.append(name)
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    
                    with frame_lock:
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
                if st.session_state.camera_active and "current_active_frame" in st.session_state:
                    with frame_lock:
                        st.session_state.frozen_frame = st.session_state.current_active_frame.copy()
                        st.session_state.frozen_issues = st.session_state.current_active_issues
                    st.toast("🎯 Frame locked!", icon="📸")
                    st.rerun()
                else:
                    st.error("🔴 Camera active nahi hai ya frame load nahi hua.")

        if st.session_state.get("frozen_frame") is not None:
            st.image(cv2.cvtColor(st.session_state.frozen_frame, cv2.COLOR_BGR2RGB), caption="Frozen Evidence")
            if st.button("📄 TRANSMIT REPORT"):
                 frozen_path = f"live_freeze_{int(time.time())}.jpg"
                 cv2.imwrite(frozen_path, st.session_state.frozen_frame)
                 for issue in st.session_state.frozen_issues:
                     generate_report(issue, location, frozen_path)

    # ... (baaki Image/Video mode wahi rahega) ...
