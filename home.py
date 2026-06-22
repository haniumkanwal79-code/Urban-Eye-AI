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
    .badge-active
