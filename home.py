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

# ================= SESSION INIT =================
if "captured_frame" not in st.session_state:
    st.session_state.captured_frame = None

if "captured_issue" not in st.session_state:
    st.session_state.captured_issue = None

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

    .card {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        padding:20px;
        border-radius:16px;
        color:white;
        text-align:center;
    }

    .metric {
        font-size:26px;
        font-weight:bold;
        color:#00ffcc;
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

    st.success("📄 Report Generated Successfully")

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇ Download Report",
            f,
            file_name="Urban_AI_Report.pdf",
            mime="application/pdf"
        )


# ================= DETECT FUNCTION =================
def detect_issues(frame):
    results = model.predict(frame, conf=0.5)

    detected = []
    annotated = results[0].plot()

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            name = model.names[cls]

            if name.lower() != "person":
                detected.append(name)

    return annotated, list(set(detected))


# ================= DASHBOARD =================
def dashboard():

    st.markdown('<div class="main-title">🚀 URBAN AI COMMAND CENTER</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Issues", "1240")
    col2.metric("Resolved", "980")
    col3.metric("Pending", "260")


# ================= IMAGE MODE =================
def image_mode():

    st.title("📡 Image Detection")

    image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    location = st.text_input("Location", "Unknown")

    if image:

        file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        annotated, detected = detect_issues(img)

        st.image(annotated, use_container_width=True)

        st.write("### Detected Issues:", detected)

        if st.button("Generate Report"):
            path = f"img_{datetime.now().timestamp()}.jpg"
            cv2.imwrite(path, img)

            for issue in detected:
                generate_report(issue, location, path)


# ================= LIVE CAMERA (FIXED + OK BUTTON) =================
def live_camera():

    st.title("🎥 Live Smart Detection")

    location = st.text_input("Location", "Auto GPS (manual fallback)")

    frame_placeholder = st.empty()

    cap = cv2.VideoCapture(0)

    run = st.checkbox("Start Camera")

    while run:

        ret, frame = cap.read()
        if not ret:
            st.error("Camera not found")
            break

        annotated, detected = detect_issues(frame)

        frame_placeholder.image(annotated, channels="BGR")

        if len(detected) > 0:

            st.warning(f"Issues Detected: {detected}")

            # SAVE FRAME FOR CONFIRMATION
            st.session_state.captured_frame = frame.copy()
            st.session_state.captured_issue = detected

            if st.button("✔ Capture This Frame (OK)"):
                path = f"live_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(path, st.session_state.captured_frame)

                for issue in st.session_state.captured_issue:
                    generate_report(issue, location, path)

                st.success("Report Generated from Selected Frame")

    cap.release()


# ================= ANALYTICS =================
def analytics():

    st.title("📊 Analytics")

    df = pd.DataFrame({
        "Category": ["Road", "Garbage", "Water", "Electricity", "Other"],
        "Reports": [320, 210, 400, 150, 160]
    })

    st.bar_chart(df.set_index("Category"))


# ================= SETTINGS =================
def settings():

    st.title("⚙️ Settings")

    st.checkbox("AI Auto Reporting")
    st.checkbox("Smart Alerts")
    st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])


# ================= MAIN =================
def show_home():

    load_css()

    menu = st.sidebar.radio(
        "🚀 Urban AI Navigation",
        ["Dashboard", "Image Mode", "Live Camera", "Analytics", "Settings"]
    )

    st.sidebar.success("System Online")

    if menu == "Dashboard":
        dashboard()

    elif menu == "Image Mode":
        image_mode()

    elif menu == "Live Camera":
        live_camera()

    elif menu == "Analytics":
        analytics()

    elif menu == "Settings":
        settings()
