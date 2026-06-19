import streamlit as st
from ultralytics import YOLO
import numpy as np
import cv2
import pandas as pd
from datetime import datetime
from pdf_utils import create_pdf
import os

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Urban AI Command Center",
    page_icon="🚀",
    layout="wide"
)

model = YOLO("best.pt")

# ================= MODERN UI CSS =================
def load_css():
    st.markdown("""
    <style>

    .main-title {
        font-size:42px;
        font-weight:800;
        color:#00D4FF;
        text-align:center;
        margin-bottom:20px;
    }

    .sub-text {
        text-align:center;
        color:#AAB4C3;
        margin-bottom:30px;
    }

    .card {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        padding:20px;
        border-radius:16px;
        box-shadow:0px 0px 12px rgba(0,0,0,0.3);
        color:white;
        text-align:center;
        transition:0.3s;
    }

    .card:hover {
        transform: scale(1.02);
        box-shadow:0px 0px 20px rgba(0,212,255,0.4);
    }

    .metric {
        font-size:28px;
        font-weight:bold;
        color:#00ffcc;
    }

    .sidebar-box {
        background:#111827;
        padding:15px;
        border-radius:10px;
        margin-bottom:10px;
        color:white;
    }

    </style>
    """, unsafe_allow_html=True)


# ================= REPORT =================
def generate_report(issue_type, location, image_path):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pdf_path = create_pdf(
        issue_type=issue_type,
        location=location,
        image_path=image_path,
        timestamp=timestamp
    )

    st.success("📄 Government-Level Report Generated")

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇ Download Official Report",
            f,
            file_name="Urban_AI_Gov_Report.pdf",
            mime="application/pdf"
        )


# ================= DASHBOARD =================
def dashboard():

    st.markdown('<div class="main-title">🚀 URBAN AI COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-text">Smart City Monitoring & Automated Issue Detection System</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="card">🔥 TOTAL ISSUES<br><div class="metric">1240</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">✅ RESOLVED<br><div class="metric">980</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card">⚠ PENDING<br><div class="metric">260</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="card">📍 ACTIVE ZONES<br><div class="metric">18</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # AI INSIGHT PANEL
    st.info("🧠 AI Insight: Most issues detected in HIGH TRAFFIC urban zones between 6PM - 10PM")


# ================= UPLOAD SECTION =================
def upload_section():

    st.title("📡 AI Vision Monitoring System")

    input_type = st.radio("Select Input Mode", ["Image", "Video", "Live Camera"])

    if input_type == "Image":

        image = st.file_uploader("Upload City Image", type=["jpg","png","jpeg"])
        location = st.text_input("📍 Location (Auto GPS ready)", "Unknown Area")

        if image:

            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            results = model.predict(img, conf=0.5)
            annotated = results[0].plot()

            st.image(annotated, caption="AI Detection Output", use_container_width=True)

            detected = []

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    name = model.names[cls]
                    if name.lower() != "person":
                        detected.append(name)

            detected = list(set(detected))

            st.success("Detection Completed ✔")

            st.write("### 🚨 Detected Issues")
            for d in detected:
                st.write("🔴", d)

            if st.button("📄 Generate Government Report"):

                img_path = f"report_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, img)

                for issue in detected:
                    generate_report(issue, location, img_path)

    elif input_type == "Video":
        st.info("Video intelligence module upgrading... 🚧")

    elif input_type == "Live Camera":
        st.warning("Live surveillance mode (Beta)")


# ================= ANALYTICS =================
def analytics():

    st.title("📊 National Urban Analytics")

    df = pd.DataFrame({
        "Sector": ["Road", "Garbage", "Water", "Electricity", "Other"],
        "Reports": [320, 210, 400, 150, 160]
    })

    st.bar_chart(df.set_index("Sector"))

    st.success("📊 Trend: Road & Water issues are increasing in metropolitan zones")


# ================= SETTINGS =================
def settings():

    st.title("⚙️ System Control Panel")

    st.checkbox("Enable AI Auto Reporting")
    st.checkbox("Enable Smart Alerts")
    st.checkbox("Dark Mode (UI)")
    st.selectbox("Priority Mode", ["Low", "Medium", "High", "Critical"])


# ================= MAIN APP =================
def show_home():

    load_css()

    menu = st.sidebar.radio(
        "🚀 Urban AI Navigation",
        ["🏠 Command Dashboard", "📡 Detection System", "📊 Analytics", "⚙️ Settings"]
    )

    st.sidebar.markdown("---")
    st.sidebar.success("🟢 System Online")
    st.sidebar.info("AI Model: YOLOv8 Active")

    if menu == "🏠 Command Dashboard":
        dashboard()

    elif menu == "📡 Detection System":
        upload_section()

    elif menu == "📊 Analytics":
        analytics()

    elif menu == "⚙️ Settings":
        settings()
