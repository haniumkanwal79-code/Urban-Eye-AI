import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import folium
from streamlit_folium import st_folium
from datetime import datetime
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Urban AI Pro Dashboard",
    page_icon="🚧",
    layout="wide"
)

# ---------------- CUSTOM UI ----------------
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Arial';
}

.main-title {
    font-size: 42px;
    text-align: center;
    color: #00E5FF;
    animation: glow 2s infinite alternate;
}

@keyframes glow {
    from {text-shadow: 0 0 10px #00E5FF;}
    to {text-shadow: 0 0 25px #00E5FF;}
}

.card {
    background: rgba(0,0,0,0.6);
    padding: 15px;
    border-radius: 15px;
    margin: 10px 0;
    border-left: 5px solid #00E5FF;
}

.metric {
    font-size: 20px;
    color: white;
}

.big-number {
    font-size: 32px;
    color: #00E5FF;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    return YOLO("best.pt")   # your trained model

model = load_model()

# ---------------- SESSION STATE ----------------
if "count" not in st.session_state:
    st.session_state.count = 0

# ---------------- TITLE ----------------
st.markdown('<div class="main-title">🚧 Urban AI Detection System</div>', unsafe_allow_html=True)

# ---------------- LAYOUT ----------------
col1, col2, col3 = st.columns([1,2,1])

# ---------------- LEFT PANEL ----------------
with col1:
    st.markdown("## 📥 Input Panel")

    file = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])

    run = st.button("🚀 Run Detection")

# ---------------- CENTER PANEL ----------------
with col2:

    st.markdown("## 🧠 Detection Output")

    placeholder = st.empty()

# ---------------- RIGHT PANEL ----------------
with col3:

    st.markdown("## 📊 Live Stats")

    st.markdown(f"""
    <div class="card">
        <div class="metric">Total Issues Detected</div>
        <div class="big-number">{st.session_state.count}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- MAP ----------------
st.markdown("## 🗺️ Location View")

m = folium.Map(location=[33.6844, 73.0479], zoom_start=12)
st_folium(m, width=1000, height=400)

# ---------------- DETECTION ----------------
if file and run:

    image = Image.open(file)

    st.image(image, caption="Uploaded Image", use_container_width=True)

    with st.spinner("🔍 Detecting issues..."):
        time.sleep(0.5)  # smooth animation effect

        results = model.predict(image, conf=0.5)

        plotted = results[0].plot()

        detections = results[0].boxes

        st.session_state.count += len(detections)

    # Show result
    placeholder.image(plotted, caption="Detected Output", use_container_width=True)

    # Animated cards
    for box in detections:

        cls = int(box.cls[0])
        conf = float(box.conf[0])

        label = model.names[cls]

        st.markdown(f"""
        <div class="card">
            🚨 Issue: <b>{label}</b><br>
            🎯 Confidence: <b>{conf:.2f}</b><br>
            ⏱ Time: {datetime.now().strftime("%H:%M:%S")}
        </div>
        """, unsafe_allow_html=True)

    st.success("Detection Completed Successfully 🚀")
