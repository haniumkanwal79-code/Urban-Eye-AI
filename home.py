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

# Gemini SDK (New Client Architecture)
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
