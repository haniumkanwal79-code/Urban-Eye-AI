import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Urban Eye AI",
    page_icon="🚧",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1e3a8a;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    model = YOLO("yolo11s.pt")   # or best.pt
    return model

model = load_model()

# ---------------- DEPARTMENT MAP ----------------
DEPARTMENT_MAP = {
    'pothole': 'Public Works Department',
    'garbage': 'Sanitation Department',
    'graffiti': 'Municipal Corporation',
    'broken_tree': 'Forestry Department',
    'fallen_pole': 'Electricity Department'
}

# ---------------- HELPER FUNCTIONS ----------------
def process_detections(results):
    detections = []

    for r in results.boxes:
        cls = int(r.cls[0])
        conf = float(r.conf[0])

        detections.append({
            "class": model.names[cls],
            "confidence": conf
        })

    return detections

def display_results(detections):
    st.subheader("📋 Detection Results")

    if len(detections) == 0:
        st.warning("No objects detected")
        return

    for det in detections:
        issue = det["class"]
        confidence = det["confidence"]

        dept = DEPARTMENT_MAP.get(issue, "General Department")

        st.success(
            f"✅ {issue} detected | Confidence: {confidence:.2f} | Assigned: {dept}"
        )

def generate_report(detections, lat, lng):
    report = f"""
URBAN ISSUE DETECTION REPORT
Generated: {datetime.now()}

Location:
Latitude: {lat}
Longitude: {lng}

Detected Issues:
"""

    for det in detections:
        report += f"\n- {det['class']} ({det['confidence']:.2f})"

    return report

# ---------------- HEADER ----------------
st.markdown(
    '<h1 class="main-header">🚧 Urban Eye AI Dashboard</h1>',
    unsafe_allow_html=True
)

st.markdown("### AI Powered Urban Issue Detection System")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📍 Location")

lat = st.sidebar.number_input("Latitude", value=19.0760)
lng = st.sidebar.number_input("Longitude", value=72.8777)

# ---------------- MAIN LAYOUT ----------------
left_col, right_col = st.columns([1, 2])

# ---------------- LEFT COLUMN ----------------
with left_col:

    st.header("📥 Upload Input")

    input_type = st.radio(
        "Choose Input Type",
        ["Image", "Video", "Live Stream"]
    )

    # ---------- IMAGE ----------
    if input_type == "Image":

        uploaded_file = st.file_uploader(
            "Upload Image",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file:

            image = Image.open(uploaded_file)

            st.image(image, caption="Uploaded Image")

            if st.button("🔍 Detect Objects"):

                results = model.predict(image, conf=0.5)

                detections = process_detections(results[0])

                plotted = results[0].plot()

                st.image(plotted, caption="Detection Result")

                display_results(detections)

                report = generate_report(detections, lat, lng)

                st.download_button(
                    label="📄 Download Report",
                    data=report,
                    file_name="urban_report.txt",
                    mime="text/plain"
                )

    # ---------- VIDEO ----------
    elif input_type == "Video":

        uploaded_video = st.file_uploader(
            "Upload Video",
            type=["mp4", "avi", "mov"]
        )

        if uploaded_video:
            st.video(uploaded_video)

            st.info("Video detection feature coming soon")

    # ---------- LIVE STREAM ----------
    elif input_type == "Live Stream":

        st.warning("Live stream feature coming soon")

# ---------------- RIGHT COLUMN ----------------
with right_col:

    st.header("🗺️ Location Map")

    m = folium.Map(location=[lat, lng], zoom_start=15)

    folium.Marker(
        [lat, lng],
        popup="Issue Location",
        tooltip="Urban Issue",
        icon=folium.Icon(color="red")
    ).add_to(m)

    st_folium(m, width=700, height=500)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("### 🚀 Powered by YOLO11 + Streamlit")
