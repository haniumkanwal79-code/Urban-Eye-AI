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
    page_title="Urban AI Smart Dashboard",
    page_icon="🚀",
    layout="wide"
)

# ================= LOAD MODEL =================
model = YOLO("best.pt")


# ================= CSS (MODERN UI) =================
def load_css():
    st.markdown("""
    <style>
    .main-title {
        font-size:40px;
        font-weight:700;
        color:#00C2FF;
    }
    .card {
        padding:20px;
        border-radius:15px;
        background:#111827;
        color:white;
        margin-bottom:10px;
    }
    .metric-box {
        background:#1f2937;
        padding:15px;
        border-radius:10px;
        text-align:center;
    }
    </style>
    """, unsafe_allow_html=True)


# ================= REPORT GENERATOR =================
def generate_report(issue_type, location, image_path):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pdf_path = create_pdf(
        issue_type=issue_type,
        location=location,
        image_path=image_path,
        timestamp=timestamp
    )

    st.success("📄 Professional Report Generated!")

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="⬇ Download Smart Report",
            data=f,
            file_name="Urban_AI_Report.pdf",
            mime="application/pdf"
        )


# ================= HOME DASHBOARD =================
def dashboard():

    st.markdown('<div class="main-title">🚀 Urban AI Smart City Dashboard</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-box">🔥 Total Issues<br><h2>1240</h2></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-box">✅ Resolved<br><h2>980</h2></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-box">⚠ Pending<br><h2>260</h2></div>', unsafe_allow_html=True)


# ================= UPLOAD SECTION =================
def upload_section():

    st.title("📥 AI Issue Detection System")

    input_type = st.radio("Select Input Type", ["Image", "Video", "Live Camera"])

    # ================= IMAGE =================
    if input_type == "Image":

        image = st.file_uploader("Upload City Image", type=["jpg", "png", "jpeg"])
        location = st.text_input("📍 Location", "Unknown Area")

        if image:

            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            results = model.predict(img, conf=0.5)
            annotated = results[0].plot()

            st.image(annotated, caption="AI Detection Result", use_container_width=True)

            st.success("Detection Completed ✔")

            detected_classes = []

            for r in results:
                for box in r.boxes:

                    cls_id = int(box.cls[0])
                    class_name = model.names[cls_id]

                    if class_name.lower() != "person":
                        detected_classes.append(class_name)

            detected_classes = list(set(detected_classes))

            st.write("### Detected Issues:")
            for d in detected_classes:
                st.write("🔴", d)

            if st.button("🚨 Generate Smart Report"):

                image_path = f"report_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(image_path, img)

                for issue in detected_classes:
                    generate_report(issue, location, image_path)


    # ================= VIDEO =================
    elif input_type == "Video":
        video = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
        if video:
            st.video(video)
            st.info("Video analysis coming in next update 🚀")


    # ================= LIVE =================
    elif input_type == "Live Camera":
        st.warning("Live mode enabled (basic preview only)")
        st.info("Use image mode for accurate reporting")


# ================= ANALYTICS =================
def analytics():

    st.title("📊 Analytics Dashboard")

    data = pd.DataFrame({
        "Category": ["Road", "Garbage", "Street Light", "Water", "Other"],
        "Reports": [320, 210, 150, 400, 160]
    })

    st.bar_chart(data.set_index("Category"))


# ================= SETTINGS =================
def settings():

    st.title("⚙️ System Settings")

    st.checkbox("🔔 Enable Notifications")
    st.checkbox("🌙 Dark Mode (UI)")
    st.selectbox("Priority Level", ["Low", "Medium", "High"])


# ================= MAIN APP =================
def show_home():

    load_css()

    menu = st.sidebar.radio(
        "🚀 Urban AI Menu",
        ["🏠 Dashboard", "📥 Detect Issues", "📊 Analytics", "⚙️ Settings"]
    )

    st.sidebar.success("Smart City AI System")

    if menu == "🏠 Dashboard":
        dashboard()

    elif menu == "📥 Detect Issues":
        upload_section()

    elif menu == "📊 Analytics":
        analytics()

    elif menu == "⚙️ Settings":
        settings()
