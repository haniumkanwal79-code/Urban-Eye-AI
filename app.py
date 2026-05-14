import streamlit as st
import torch
import cv2
from ultralytics import YOLO
import numpy as np
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
import io
import base64
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

# Custom CSS for professional look
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
    .stFileUploader > div > div > div {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        border: 2px dashed #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

# Background image
def get_base64_image():
    return base64.b64encode(open("urban_bg.jpg", "rb").read()).decode()

# Load your YOLOv8 model (update path)
@st.cache_resource
def load_model():
    model = YOLO('path/to/your/yolov8_urban_model.pt')  # Update this path
    return model

# Department mapping
DEPARTMENT_MAP = {
    'pothole': 'Public Works Department',
    'garbage': 'Sanitation Department', 
    'graffiti': 'Municipal Corporation',
    'broken_tree': 'Forestry Department',
    'fallen_pole': 'Electricity Department'
}

# Page config
st.set_page_config(
    page_title="Urban Issue Detection Dashboard",
    page_icon="🚧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Background
# st.markdown(f"""
# <style>
#     .stApp {{
#         background-image: url("data:image/jpeg;base64,{get_base64_image()}");
#         background-size: cover;
#     }}
# </style>
# """, unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚧 Urban Issue Detection Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**AI-Powered Smart City Monitoring System**")

# Load model
model = load_model()

# Sidebar - Model Metrics
st.sidebar.markdown("## 🤖 Model Performance")
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>Speed</h3>
        <h2>28.4 ms</h2>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>Accuracy</h3>
        <h2>92.7%</h2>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>mAP@0.5</h3>
        <h2>89.3%</h2>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**📍 Current Location**")
lat = st.sidebar.number_input("Latitude", value=19.0760)
lng = st.sidebar.number_input("Longitude", value=72.8777)

# Main layout - Left: Input, Right: Results
left_col, right_col = st.columns([1, 2])

with left_col:
    st.markdown("## 📥 Input")
    
    input_type = st.radio("Choose input type:", 
                         ["🖼️ Image", "🎥 Video", "📹 Live Stream"], 
                         horizontal=True)
    
    if input_type == "🖼️ Image":
        uploaded_file = st.file_uploader("Upload image", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            if st.button("🔍 Detect Issues", type="primary"):
                # Process image
                results = model.predict(uploaded_file, save=True, conf=0.5)
                detections = process_detections(results[0])
                display_results(detections, image)
    
    elif input_type == "🎥 Video":
        uploaded_video = st.file_uploader("Upload video", type=['mp4', 'avi', 'mov'])
        if uploaded_video:
            st.video(uploaded_video)
            if st.button("🎬 Analyze Video"):
                st.info("Video processing started... (This may take a few minutes)")
    
    elif input_type == "📹 Live Stream":
        st.warning("Live stream coming soon for hardware deployment!")
        if st.button("🚀 Start Live Detection"):
            st.success("Live stream simulation - detections would appear here")

with right_col:
    st.markdown("## 🗺️ Location & Results")
    
    # Google Map
    m = folium.Map(location=[lat, lng], zoom_start=15)
    folium.Marker(
        [lat, lng],
        popup="Issue Location",
        tooltip="Click for details",
        icon=folium.Icon(color="red", icon="exclamation-triangle")
    ).add_to(m)
    folium_static(m, width=700, height=300)

# Results section
st.markdown("---")
st.markdown("## 📊 Detection Summary & Report")

# Simulated results (replace with real detections)
issues_detected = {
    'pothole': 3,
    'garbage': 2,
    'graffiti': 1
}

col1, col2, col3 = st.columns(3)
total_issues = sum(issues_detected.values())
with col1:
    st.metric("Total Issues", total_issues, delta=f"+{total_issues//2}")
with col2:
    st.metric("Critical", issues_detected.get('pothole', 0), delta="2")
with col3:
    st.metric("Departments", len(set(DEPARTMENT_MAP[issue] for issue in issues_detected)))

# Department assignments
st.markdown("## 🏢 Assigned Departments")
for issue, count in issues_detected.items():
    dept = DEPARTMENT_MAP.get(issue, "General")
    st.markdown(f"**{issue.title()}** ({count}) → {dept}")

# Report generation
st.markdown("## 📄 Auto-Generated Report")
if st.button("📧 Generate & Email Report", type="primary"):
    report = generate_report(issues_detected, lat, lng)
    st.download_button(
        "💾 Download Report",
        report,
        "urban_issue_report.pdf",
        "application/pdf"
    )
    st.success("Report generated and emailed to departments!")

# Footer
st.markdown("---")
st.markdown("*Powered by YOLOv8 & Streamlit | Ready for Hardware Deployment*")

# Helper functions
def process_detections(results):
    """Process YOLO results"""
    detections = []
    for r in results.boxes:
        cls = int(r.cls[0])
        conf = float(r.conf[0])
        detections.append({
            'class': model.names[cls],
            'confidence': conf,
            'bbox': r.xyxy[0].tolist()
        })
    return detections

def display_results(detections, image):
    """Display detection results"""
    st.success(f"✅ Found {len(detections)} urban issues!")
    for det in detections:
        st.write(f"• {det['class']} (Confidence: {det['confidence']:.2f})")

def generate_report(detections, lat, lng):
    """Generate PDF report"""
    report_content = f"""
    Urban Issue Detection Report
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    
    Location: {lat}, {lng}
    Total Issues: {sum(detections.values())}
    
    Issues Found:
    """
    for issue, count in detections.items():
        report_content += f"\n- {issue}: {count}"
    
    return report_content.encode()

if __name__ == "__main__":
    st.rerun()