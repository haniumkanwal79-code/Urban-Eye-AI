import streamlit as st
from ultralytics import YOLO
import numpy as np
import cv2
import pandas as pd
from datetime import datetime
from pdf_utils import create_pdf

import folium
from streamlit_folium import st_folium

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Urban AI Command Center PRO",
    page_icon="🚀",
    layout="wide"
)

model = YOLO("best.pt")

# ================= SESSION STORAGE =================
if "logs" not in st.session_state:
    st.session_state.logs = []

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

# ================= CSS =================
def load_css():
    st.markdown("""
    <style>
    .title {
        font-size:40px;
        font-weight:800;
        text-align:center;
        color:#00D4FF;
    }

    .sub {
        text-align:center;
        color:#94a3b8;
        margin-bottom:20px;
    }

    .card {
        background: linear-gradient(135deg,#0f172a,#1e293b);
        padding:20px;
        border-radius:16px;
        color:white;
        text-align:center;
    }

    .big {
        font-size:26px;
        font-weight:bold;
        color:#22d3ee;
    }
    </style>
    """, unsafe_allow_html=True)


# ================= GPS LOCATION (browser) =================
def get_location_js():
    loc = st.components.v1.html("""
    <script>
    navigator.geolocation.getCurrentPosition(
        function(pos){
            const coords = pos.coords.latitude + "," + pos.coords.longitude;
            window.parent.postMessage(coords, "*");
        }
    );
    </script>
    """, height=0)
    return loc


# ================= REPORT =================
def generate_report(issue, location, image_path, severity):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pdf_path = create_pdf(
        issue_type=issue,
        location=location,
        image_path=image_path,
        timestamp=timestamp,
        severity=severity
    )

    st.session_state.logs.append({
        "issue": issue,
        "location": location,
        "severity": severity,
        "time": timestamp
    })

    with open(pdf_path, "rb") as f:
        st.download_button("⬇ Download Govt Report", f, file_name="report.pdf")


# ================= DASHBOARD =================
def dashboard():

    st.markdown('<div class="title">🚀 SMART CITY COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">Real-Time Urban Monitoring & AI Surveillance System</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🔥 Total Issues", len(st.session_state.logs))
    col2.metric("⚠ High Risk", sum(1 for x in st.session_state.logs if x.get("severity") == "High"))
    col3.metric("🚨 Critical", sum(1 for x in st.session_state.logs if x.get("severity") == "Critical"))
    col4.metric("📍 Active Zones", "12")

    st.markdown("---")

    st.info("🧠 AI Insight: High severity issues mostly detected in dense traffic zones")

    # Timeline
    st.subheader("📜 Recent Activity")
    st.dataframe(pd.DataFrame(st.session_state.logs[-10:]))


# ================= MAP =================
def show_map():

    st.subheader("📍 Live Urban Issue Map")

    m = folium.Map(location=[31.5, 74.3], zoom_start=6)

    for log in st.session_state.logs:

        folium.Marker(
            location=[31.5, 74.3],
            popup=f"{log['issue']} | {log['severity']}",
            icon=folium.Icon(color="red" if log["severity"]=="Critical" else "blue")
        ).add_to(m)

    st_folium(m, width=900, height=400)


# ================= UPLOAD =================
def upload_section():

    st.title("📡 AI Detection System")

    input_type = st.radio("Input Mode", ["Image", "Video"])

    location = st.text_input("📍 Location (auto GPS coming soon)", "Unknown")

    if input_type == "Image":

        image = st.file_uploader("Upload Image")

        if image:

            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            results = model.predict(img, conf=0.5)
            st.image(results[0].plot(), use_container_width=True)

            issues = []

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    name = model.names[cls]
                    if name.lower() != "person":
                        issues.append(name)

            issues = list(set(issues))

            st.success("Detection Done")

            for i in issues:
                severity = "High" if i in ["fire", "accident"] else "Medium"

                if st.button(f"Generate Report: {i}"):

                    img_path = f"{i}.jpg"
                    cv2.imwrite(img_path, img)

                    generate_report(i, location, img_path, severity)


# ================= ANALYTICS =================
def analytics():

    st.title("📊 Analytics")

    df = pd.DataFrame({
        "Type": ["Road", "Garbage", "Water", "Electricity"],
        "Reports": [320, 210, 400, 150]
    })

    st.bar_chart(df.set_index("Type"))


# ================= MAIN =================
def show_home():

    load_css()

    menu = st.sidebar.radio(
        "🚀 CONTROL PANEL",
        ["Dashboard", "Detection", "Map", "Analytics"]
    )

    if menu == "Dashboard":
        dashboard()

    elif menu == "Detection":
        upload_section()

    elif menu == "Map":
        show_map()

    elif menu == "Analytics":
        analytics()
