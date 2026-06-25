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
from streamlit_js_eval import get_geolocation # Nayi library

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

# ================= HELPER: GEO-TAGGING =================
def get_location_link():
    """Browser se GPS coordinates fetch karne ke liye"""
    loc = get_geolocation()
    if loc and 'coords' in loc:
        lat = loc['coords']['latitude']
        lng = loc['coords']['longitude']
        maps_link = f"https://www.google.com/maps?q={lat},{lng}"
        return maps_link, f"{lat}, {lng}"
    return None, "GPS Data Unavailable"

# ================= PAGE CONFIG =================
def init_page_config():
    try:
        st.set_page_config(
            page_title="Urban Eye AI - Control Center",
            page_icon="👁️",
            layout="wide"
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

# ================= CSS =================
def load_css():
    st.markdown("""
    <style>
    .premium-brand-card { background: linear-gradient(135deg, #090d16 0%, #111827 100%); padding: 25px; border-radius: 16px; margin-bottom: 30px; text-align: center; }
    .stButton button { background: linear-gradient(93deg, #00e5ff 0%, #00b4d8 100%) !important; color: #090d16 !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# ================= AI & REPORTING =================
def generate_ai_action_plan(issue_type, location):
    try:
        api_key = st.secrets["gemini"]["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        prompt = f"Issue: {issue_type} at {location}. Provide 3 bullet point action plan for field workers. Under 60 words."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except:
        return "Deploy rapid response unit to location immediately."

def send_report_email(department_email, issue_type, location, timestamp, pdf_path, ai_plan, maps_link):
    sender_email = st.secrets["email"]["SENDER_EMAIL"]
    sender_password = st.secrets["email"]["APP_PASSWORD"]
    
    msg = MIMEMultipart()
    msg['Subject'] = f"[URGENT] {issue_type.upper()} Detected"
    body = f"Incident: {issue_type}\nLocation: {location}\nMap Link: {maps_link}\n\nAction Plan:\n{ai_plan}"
    msg.attach(MIMEText(body, 'plain'))
    # ... (PDF attachment logic remains same as your original code) ...
    # ... (SMTP server logic remains same as your original code) ...
    return True

def generate_report(issue_type, location, image_path):
    from pdf_utils import create_pdf
    
    # Geo-tagging capture
    maps_link, coords = get_location_link()
    loc_display = f"{location} | Coordinates: {coords}"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ai_plan = generate_ai_action_plan(issue_type, loc_display)
    
    # PDF generation logic
    pdf_path = create_pdf(issue_type=issue_type, location=loc_display, image_path=image_path, timestamp=timestamp)
    
    # Email
    department_email = "dispatch@city.gov"
    send_report_email(department_email, issue_type, loc_display, timestamp, pdf_path, ai_plan, maps_link)
    
    st.success(f"Report generated for {issue_type}. Location pinned: {maps_link}")

# ================= MAIN APP =================
def main():
    init_page_config()
    load_css()
    
    if "incident_db" not in st.session_state:
        st.session_state.incident_db = []

    st.sidebar.title("🏛 Urban Eye AI")
    menu = st.sidebar.radio("Navigation", ["Dashboard", "Surveillance Grid"])
    
    if menu == "Dashboard":
        st.title("Control Center")
        # Add your dashboard code here
        
    elif menu == "Surveillance Grid":
        st.title("📡 Surveillance Grid")
        # Yahan jab detection ho aur report button click ho, 
        # toh upar wala generate_report(issue, location, path) call karein.

if __name__ == "__main__":
    main()
