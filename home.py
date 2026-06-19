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
    layout="wide"
)

model = YOLO("best.pt")


# ================= CSS =================
def load_css():
    st.markdown("""
    <style>
    .gov-title {
        font-size:40px;
        font-weight:900;
        text-align:center;
        color:#00e5ff;
    }
    .gov-card {
        background:#111827;
        padding:20px;
        border-radius:15px;
        color:white;
        text-align:center;
        border:1px solid #1f2a44;
    }
    .metric {
        font-size:28px;
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

    st.success("🏛 Report Generated")

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇ Download Report",
            f,
            file_name="gov_report.pdf",
            mime="application/pdf"
        )


# ================= DASHBOARD =================
def dashboard():
    st.markdown('<div class="gov-title">🏛 URBAN AI COMMAND CENTER</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="gov-card">TOTAL<br><div class="metric">1240</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="gov-card">RESOLVED<br><div class="metric">980</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="gov-card">PENDING<br><div class="metric">260</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="gov-card">ZONES<br><div class="metric">18</div></div>', unsafe_allow_html=True)


# ================= UPLOAD SYSTEM =================
def upload_section():

    st.title("📡 Detection System")

    mode = st.radio("Select Mode", ["Image", "Video", "Live Camera"])

    # ================= IMAGE =================
    if mode == "Image":

        image = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])
        location = st.text_input("Location", "Unknown")

        if image:

            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            results = model.predict(img, conf=0.5)

            annotated = results[0].plot()

            st.image(annotated)

            detected = []

            for r in results:
                for box in r.boxes:
                    name = model.names[int(box.cls[0])]
                    if name.lower() != "person":
                        detected.append(name)

            detected = list(set(detected))

            st.success("Detection Done")

            if st.button("Generate Report"):
                path = f"img_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(path, img)

                for d in detected:
                    generate_report(d, location, path)

    # ================= VIDEO (FULL FIXED SYSTEM) =================
    elif mode == "Video":

        st.subheader("🎥 Video AI Analysis System (ACTIVE)")

        video_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])

        location = st.text_input("Location", "Unknown")

        if video_file:

            temp_path = "temp_video.mp4"

            with open(temp_path, "wb") as f:
                f.write(video_file.read())

            cap = cv2.VideoCapture(temp_path)

            stframe = st.empty()

            detected_all = []

            while cap.isOpened():

                ret, frame = cap.read()
                if not ret:
                    break

                results = model.predict(frame, conf=0.5)

                annotated = results[0].plot()

                stframe.image(annotated, channels="BGR")

                for r in results:
                    for box in r.boxes:
                        name = model.names[int(box.cls[0])]
                        if name.lower() != "person":
                            detected_all.append(name)

            cap.release()

            detected_all = list(set(detected_all))

            st.success("Video Analysis Complete ✔")

            if st.button("Generate Video Report"):

                img_path = f"video_frame_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, frame)

                for d in detected_all:
                    generate_report(d, location, img_path)

    # ================= LIVE CAMERA =================
    elif mode == "Live Camera":

        st.warning("LIVE MODE ACTIVE")

        location = st.text_input("Location", "Unknown")

        class Live(VideoTransformerBase):

            def transform(self, frame):

                img = frame.to_ndarray(format="bgr24")

                results = model.predict(img, conf=0.5)

                for r in results:
                    for box in r.boxes:
                        name = model.names[int(box.cls[0])]

                        if name.lower() != "person":
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
                            cv2.putText(img, name, (x1,y1-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                        (0,255,0), 2)

                return img

        webrtc_streamer(
            key="live",
            video_transformer_factory=Live,
            media_stream_constraints={"video": True, "audio": False}
        )


# ================= ANALYTICS =================
def analytics():
    st.title("Analytics")

    df = pd.DataFrame({
        "Category": ["Road", "Garbage", "Water", "Light", "Other"],
        "Reports": [320,210,400,150,160]
    })

    st.bar_chart(df.set_index("Category"))


# ================= SETTINGS =================
def settings():
    st.title("Settings")
    st.checkbox("Alerts")
    st.checkbox("Dark Mode")


# ================= MAIN =================
def show_home():

    load_css()

    menu = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Detection", "Analytics", "Settings"]
    )

    if menu == "Dashboard":
        dashboard()

    elif menu == "Detection":
        upload_section()

    elif menu == "Analytics":
        analytics()

    elif menu == "Settings":
        settings()
