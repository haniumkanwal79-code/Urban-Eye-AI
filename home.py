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

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="🏛 National Urban Intelligence System",
    page_icon="🏛",
    layout="wide",
    initial_sidebar_state="expanded"
)

model = YOLO("best.pt")


# ================= CSS =================
def load_css():

    st.markdown("""
    <style>

    body {
        background: #0b1220;
    }

    .gov-title {
        font-size:44px;
        font-weight:900;
        text-align:center;
        color:#00e5ff;
        letter-spacing:2px;
        margin-bottom:5px;
    }

    .gov-subtitle {
        text-align:center;
        color:#9fb3c8;
        margin-bottom:30px;
        font-size:16px;
    }

    .gov-card {
        background: linear-gradient(135deg, #0f172a, #111c33);
        padding:22px;
        border-radius:18px;
        box-shadow:0px 0px 20px rgba(0,229,255,0.08);
        color:white;
        text-align:center;
        border:1px solid rgba(0,229,255,0.1);
        transition:0.3s;
    }

    .gov-card:hover {
        transform: scale(1.03);
        box-shadow:0px 0px 25px rgba(0,229,255,0.25);
    }

    .metric-big {
        font-size:30px;
        font-weight:900;
        color:#00ffcc;
    }

    .alert-box {
        background:#1b1f36;
        border-left:5px solid #00e5ff;
        padding:12px;
        border-radius:10px;
        color:white;
    }

    </style>
    """, unsafe_allow_html=True)


# ================= SAFE REPORT SYSTEM (FIXED ERROR HANDLING) =================
def generate_report(issue_type, location, image_path):

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # SAFE PDF GENERATION (FIX TYPE ERROR)
        pdf_path = create_pdf(
            issue_type=str(issue_type),
            location=str(location),
            image_path=str(image_path),
            timestamp=str(timestamp)
        )

        st.success("🏛 Official Government Report Generated")

        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇ Download Official Report (Gov Format)",
                    f,
                    file_name="National_Urban_Report.pdf",
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"Report Generation Error: {e}")


# ================= DASHBOARD =================
def dashboard():

    st.markdown('<div class="gov-title">🏛 NATIONAL URBAN INTELLIGENCE CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="gov-subtitle">Real-Time Smart City Monitoring & Automated Enforcement System</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="gov-card">🔥 TOTAL INCIDENTS<br><div class="metric-big">1240</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="gov-card">✅ RESOLVED CASES<br><div class="metric-big">980</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="gov-card">⚠ ACTIVE ALERTS<br><div class="metric-big">260</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="gov-card">📍 MONITORED ZONES<br><div class="metric-big">18</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="alert-box">
    🧠 AI GOVERNMENT INSIGHT:  
    High violation density detected in metropolitan highway zones between 6PM - 11PM.
    </div>
    """, unsafe_allow_html=True)


# ================= DETECTION =================
def upload_section():

    st.title("📡 AI Surveillance & Detection Grid")

    mode = st.radio("Select Mode", ["Image", "Video", "Live Camera"])

    # ================= IMAGE =================
    if mode == "Image":

        image = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])
        location = st.text_input("Location", "Unknown Zone")

        if image:

            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            results = model.predict(img, conf=0.5)
            annotated = results[0].plot()

            st.image(annotated, use_container_width=True)

            detected = []

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    name = model.names[cls]
                    if name.lower() != "person":
                        detected.append(name)

            detected = list(set(detected))

            st.success("Detection Completed ✔")
            st.write(detected)

            if st.button("Generate Report"):
                img_path = f"img_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, img)

                for issue in detected:
                    generate_report(issue, location, img_path)

    # ================= VIDEO (FIXED + REPORT ENABLED) =================
    elif mode == "Video":

        st.info("Video Mode Active")

        video_file = st.file_uploader("Upload Video", type=["mp4","avi","mov"])

        if video_file:

            temp_path = "temp_video.mp4"
            with open(temp_path, "wb") as f:
                f.write(video_file.read())

            cap = cv2.VideoCapture(temp_path)

            detected_all = []
            stframe = st.empty()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = model.predict(frame, conf=0.5)
                annotated = results[0].plot()

                stframe.image(annotated, channels="BGR")

                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        name = model.names[cls]
                        if name.lower() != "person":
                            detected_all.append(name)

            cap.release()

            detected_all = list(set(detected_all))
            st.success(f"Detected: {detected_all}")

            # ✅ REPORT BUTTON FOR VIDEO
            if st.button("Generate Video Report"):
                frame_path = f"video_{datetime.now().timestamp()}.jpg"

                if frame is not None:
                    cv2.imwrite(frame_path, frame)

                for issue in detected_all:
                    generate_report(issue, "Video Location", frame_path)


    # ================= LIVE CAMERA (FIXED SAFE + REPORT) =================
    elif mode == "Live Camera":

        st.warning("LIVE CAMERA ACTIVE")

        location = st.text_input("Location", "Unknown Zone")

        if "last_frame" not in st.session_state:
            st.session_state.last_frame = None
        if "last_detected" not in st.session_state:
            st.session_state.last_detected = []

        class GovCamera(VideoTransformerBase):

            def transform(self, frame):

                img = frame.to_ndarray(format="bgr24")

                results = model.predict(img, conf=0.5)

                detected = []

                for r in results:
                    for box in r.boxes:

                        cls = int(box.cls[0])
                        name = model.names[cls]

                        if name.lower() != "person":
                            detected.append(name)

                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,255), 2)

                if detected:
                    st.session_state.last_frame = img.copy()
                    st.session_state.last_detected = list(set(detected))

                return img

        webrtc_streamer(
            key="live",
            video_transformer_factory=GovCamera,
            media_stream_constraints={"video": True, "audio": False}
        )

        # ✅ SAFE CAPTURE BUTTON
        if st.button("CAPTURE REPORT"):

            if st.session_state.last_frame is not None:

                img_path = f"live_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, st.session_state.last_frame)

                for issue in st.session_state.last_detected:
                    generate_report(issue, location, img_path)

                st.success("Live Report Generated")


# ================= ANALYTICS =================
def analytics():

    st.title("Analytics")

    df = pd.DataFrame({
        "Sector": ["Road", "Garbage", "Water", "Electricity"],
        "Reports": [320, 210, 400, 150]
    })

    st.bar_chart(df.set_index("Sector"))


# ================= SETTINGS =================
def settings():

    st.title("Settings")

    st.checkbox("AI Alerts")
    st.checkbox("Logging")
    st.selectbox("Priority", ["Low", "Medium", "High"])


# ================= MAIN =================
def show_home():

    load_css()

    menu = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Surveillance", "Analytics", "Settings"]
    )

    if menu == "Dashboard":
        dashboard()

    elif menu == "Surveillance":
        upload_section()

    elif menu == "Analytics":
        analytics()

    elif menu == "Settings":
        settings()
