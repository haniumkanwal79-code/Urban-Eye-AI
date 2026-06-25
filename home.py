import os
import time
import smtplib
from datetime import datetime
import cv2
import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
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
    .premium-brand-card { background: linear-gradient(135deg, #090d16 0%, #111827 100%); border: 1px solid rgba(0, 229, 255, 0.2); border-top: 4px solid #00e5ff; padding: 25px; border-radius: 16px; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5); margin-bottom: 30px; text-align: center; }
    h1.brand-header { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: 800 !important; letter-spacing: 4px !important; color: #ffffff !important; margin: 0 !important; }
    .system-tagline { font-size: 11px !important; font-weight: 700 !important; letter-spacing: 2px !important; color: #00ffcc !important; margin-top: 6px; text-transform: uppercase; }
    .status-row { display: flex; justify-content: center; gap: 15px; margin-top: 15px; }
    .status-pill { font-size: 10px; font-weight: 700; letter-spacing: 1px; padding: 5px 12px; border-radius: 6px; text-transform: uppercase; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); color: #cbd5e1; }
    .pill-highlight { color: #00ffcc; border-color: rgba(0, 255, 204, 0.2); background: rgba(0, 255, 204, 0.02); }
    .dashboard-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.06); padding: 22px; border-radius: 14px; color: #94a3b8; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; text-align: center; transition: all 0.3s ease; }
    .dashboard-card:hover { border-color: rgba(0, 229, 255, 0.3); transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0, 229, 255, 0.08); }
    .metric-value { font-size: 32px !important; font-weight: 800 !important; color: #ffffff !important; margin-top: 5px; letter-spacing: -0.5px; }
    .panel-info-box { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #00e5ff; border-radius: 12px; padding: 16px 20px; color: #94a3b8; font-size: 13.5px; line-height: 1.6; margin-bottom: 25px; }
    .panel-info-box strong { color: #ffffff; font-weight: 600; }
    div[data-testid="stWidgetLabel"] p { color: #e2e8f0 !important; font-weight: 600 !important; font-size: 13px !important; }
    .stTextInput input { background-color: #090d16 !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 10px !important; color: #ffffff !important; }
    .stButton button { background: linear-gradient(93deg, #00e5ff 0%, #00b4d8 100%) !important; color: #090d16 !important; font-weight: 700 !important; letter-spacing: 1px !important; border: none !important; border-radius: 10px !important; padding: 12px !important; }
    section[data-testid="stSidebar"] { background: #060913 !important; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    </style>
    """, unsafe_allow_html=True)

# ================= AI & EMAIL =================
def generate_ai_action_plan(issue_type, location):
    try:
        api_key = st.secrets["gemini"]["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        prompt = f"Issue: {issue_type} at {location}. Provide 3 short action steps."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except Exception:
        return f"Standard deployment of {issue_type} emergency unit at {location}."

def send_report_email(department_email, issue_type, location, timestamp, pdf_path, ai_plan):
    return True 

def generate_report(issue_type, location, image_path):
    from pdf_utils import create_pdf
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ai_plan = generate_ai_action_plan(issue_type, location)
    pdf_path = create_pdf(issue_type, location, image_path, timestamp)
    if "incident_db" not in st.session_state: st.session_state.incident_db = []
    st.session_state.incident_db.append({"id": f"UE-{1000+len(st.session_state.incident_db)}", "type": issue_type, "location": location, "timestamp": timestamp, "status": "🔴 Pending", "action_plan": ai_plan})
    st.success(f"Report generated for {issue_type}")

# ================= MAP COMPONENT =================
def show_map(lat=31.5204, lon=74.3587):
    m = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], popup="Incident Zone", icon=folium.Icon(color="red")).add_to(m)
    st_folium(m, width=700, height=350)

# ================= DETECTION =================
def upload_section():
    st.title("📡 AI Surveillance & Detection Grid")
    mode = st.radio("Select Mode", ["Image", "Video", "Live Camera"])
    location = st.text_input("📍 Location Coordinates (lat, lon)", "31.5204, 74.3587")
    
    # Map Integration
    try:
        lat, lon = [float(x.strip()) for x in location.split(',')]
        show_map(lat, lon)
    except:
        show_map()

    # (Detection logic continues here as before...)

# ================= DASHBOARD & REST =================
def dashboard():
    st.markdown("""<div class="premium-brand-card"><h1 class="brand-header">URBAN EYE AI</h1></div>""", unsafe_allow_html=True)
    # ... baki code waisa hi hai

def track_submissions():
    st.title("📋 Live Incident Tracking Room")
    if "incident_db" in st.session_state:
        st.dataframe(pd.DataFrame(st.session_state.incident_db))

def show_home():
    if "incident_db" not in st.session_state: st.session_state.incident_db = []
    load_css()
    menu = st.sidebar.radio("🏛 CONTROL CENTER", ["🏛 Dashboard", "📡 Surveillance Grid", "📋 Track Submissions"])
    if menu == "🏛 Dashboard": dashboard()
    elif menu == "📡 Surveillance Grid": upload_section()
    elif menu == "📋 Track Submissions": track_submissions()

if __name__ == "__main__":
    init_page_config()
    show_home()
