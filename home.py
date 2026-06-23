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
from streamlit_geolocation import streamlit_geolocation # Nayi Library

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

# ================= HELPER: GEOLOCATION =================
def get_current_location():
    location = streamlit_geolocation()
    if location and location.get("latitude"):
        return f"Lat: {location['latitude']}, Lon: {location['longitude']}"
    return None

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
    h1.brand-header { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: 800 !important; letter-spacing: 4px !important; color: #ffffff !important; margin: 0 !important; }
    .system-tagline { font-size: 11px !important; font-weight: 700 !important; letter-spacing: 2px !important; color: #00ffcc !important; margin-top: 6px; text-transform: uppercase; }
    .status-row { display: flex; justify-content: center; gap: 15px; margin-top: 15px; }
    .status-pill { font-size: 10px; font-weight: 700; letter-spacing: 1px; padding: 5px 12px; border-radius: 6px; text-transform: uppercase; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); color: #cbd5e1; }
    .pill-highlight { color: #00ffcc; border-color: rgba(0, 255, 204, 0.2); background: rgba(0, 255, 204, 0.02); }
    .dashboard-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.06); padding: 22px; border-radius: 14px; color: #94a3b8; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; text-align: center; transition: all 0.3s ease; }
    .metric-value { font-size: 32px !important; font-weight: 800 !important; color: #ffffff !important; margin-top: 5px; letter-spacing: -0.5px; }
    .panel-info-box { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #00e5ff; border-radius: 12px; padding: 16px 20px; color: #94a3b8; font-size: 13.5px; line-height: 1.6; margin-bottom: 25px; }
    .stButton button { background: linear-gradient(93deg, #00e5ff 0%, #00b4d8 100%) !important; color: #090d16 !important; font-weight: 700 !important; border-radius: 10px !important; padding: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# [... AI, EMAIL, REPORT SYSTEM FUNCTIONS HEE RAHENGE (SAME AS YOUR CODE) ...]
# (Main yahan sirf upload_section edit kar raha hoon)

# ================= DETECTION =================
def upload_section():
    st.title("📡 AI Surveillance & Detection Grid")
    mode = st.radio("Select Mode", ["Image", "Video", "Live Camera"])

    st.markdown("### 📍 Set Deployment Zone")
    col_loc1, col_loc2 = st.columns([3, 1])
    
    if "auto_loc" not in st.session_state: st.session_state.auto_loc = "Unknown Zone"
    
    with col_loc1:
        location = st.text_input("📍 Location Tag", value=st.session_state.auto_loc)
    with col_loc2:
        st.write("##")
        if st.button("📍 Fetch My Location"):
            with st.spinner("Fetching GPS..."):
                loc = get_current_location()
                if loc:
                    st.session_state.auto_loc = loc
                    st.rerun()
                else:
                    st.error("Failed to get location.")

    # ... Baki ka Image/Video/Live Camera logic wahi rahega ...
    if mode == "Image":
        image = st.file_uploader("Upload City Evidence Image", type=["jpg","png","jpeg"])
        if image:
            # ... (Wahi code jo aapka tha) ...
            pass
    # ... (Baki logic yahan aayega jo pehle tha) ...

# ================= MAIN RUN FUNCTION =================
if __name__ == "__main__":
    init_page_config()
    show_home()
