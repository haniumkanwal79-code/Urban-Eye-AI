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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- Gemini API ---
try:
    from google import genai
except ImportError:
    st.error("Please install: pip install google-genai")

# --- Configuration & Model ---
def init_page_config():
    st.set_page_config(page_title="Urban Eye AI - Control Center", page_icon="👁️", layout="wide")

@st.cache_resource
def load_yolo_model():
    return YOLO("best.pt")

model = load_yolo_model()

# --- CSS Styling ---
def load_css():
    st.markdown("""
    <style>
    .premium-brand-card { background: linear-gradient(135deg, #090d16 0%, #111827 100%); border: 1px solid #00e5ff; padding: 25px; border-radius: 16px; text-align: center; }
    .metric-value { font-size: 32px; font-weight: 800; color: #ffffff; }
    .stButton button { background: linear-gradient(93deg, #00e5ff 0%, #00b4d8 100%) !important; color: #090d16 !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Reporting Logic ---
def generate_report(issue_type, location, image_path):
    # (Simplified for integration)
    if "incident_db" not in st.session_state: st.session_state.incident_db = []
    st.session_state.incident_db.append({
        "id": f"UE-{1000 + len(st.session_state.incident_db)}", 
        "type": issue_type, 
        "location": location, 
        "status": "🔴 Pending"
    })
    st.success(f"Report Generated: {issue_type} at {location}")

# --- Surveillance Module ---
def surveillance_grid():
    st.title("📡 AI Surveillance & Detection Grid")
    mode = st.radio("Select Mode", ["Image", "Live Camera"])

    if mode == "Live Camera":
        location = st.text_input("📍 Location Tag", "City Zone")
        
        # State Initialization
        if "frozen_frame" not in st.session_state: st.session_state.frozen_frame = None
        if "camera_active" not in st.session_state: st.session_state.camera_active = False

        class GovCamera(VideoTransformerBase):
            def transform(self, frame):
                img = frame.to_ndarray(format="bgr24")
                st.session_state.camera_active = True
                
                # YOLO Prediction
                results = model.predict(img, conf=0.5, verbose=False)
                detected = []
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        name = model.names[cls]
                        if name.lower() != "person":
                            detected.append(name)
                        # Draw boxes
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
                
                st.session_state.current_frame = img.copy()
                st.session_state.current_detected = list(set(detected))
                return img

        webrtc_streamer(key="gov-live", video_transformer_factory=GovCamera,
                        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

        # Controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⏸️ FREEZE & CAPTURE"):
                if st.session_state.camera_active:
                    st.session_state.frozen_frame = st.session_state.current_frame.copy()
                    st.session_state.frozen_issues = st.session_state.current_detected
                else:
                    st.error("Camera abhi start nahi hua. START button dabayein.")
        
        with col2:
            if st.button("🔄 CLEAR"):
                st.session_state.frozen_frame = None

        # Evidence Display
        if st.session_state.frozen_frame is not None:
            st.image(cv2.cvtColor(st.session_state.frozen_frame, cv2.COLOR_BGR2RGB), use_container_width=True)
            if st.button("🚀 TRANSMIT REPORT"):
                path = f"evidence_{int(time.time())}.jpg"
                cv2.imwrite(path, st.session_state.frozen_frame)
                for issue in st.session_state.frozen_issues:
                    generate_report(issue, location, path)

# --- Main App ---
def main():
    init_page_config()
    load_css()
    if "incident_db" not in st.session_state: st.session_state.incident_db = []
    
    menu = st.sidebar.radio("CONTROL CENTER", ["Dashboard", "Surveillance Grid"])
    
    if menu == "Dashboard":
        st.title("🏛️ Executive Dashboard")
        st.metric("Total Incidents", len(st.session_state.incident_db))
    else:
        surveillance_grid()

if __name__ == "__main__":
    main()
