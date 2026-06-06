import streamlit as st
from ultralytics import YOLO
import numpy as np
import cv2

model = YOLO("best.pt")

def show_home():

    # ================= SIDEBAR =================
    st.sidebar.title("🚀 Navigation")

    menu = st.sidebar.radio(
        "Go to:",
        ["Home", "Upload Issue", "Analytics", "Settings"]
    )

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ================= HOME PAGE =================
    if menu == "Home":

        st.markdown(
            '<div class="main-title">🚀 Urban Issue Reporter</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">Smart AI-Based Complaint & Monitoring System</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="card">
                <h2>📍 Reports</h2>
                <p>Total issue reports submitted by users.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="card">
                <h2>🤖 AI Detection</h2>
                <p>Automatic issue analysis using AI models.</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="card">
                <h2>📊 Analytics</h2>
                <p>Track complaints and department performance.</p>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Complaints", "1,240")
        m2.metric("Resolved", "980")
        m3.metric("Pending", "260")

    # ================= UPLOAD ISSUE =================
    elif menu == "Upload Issue":

        st.title("📥 Upload Issue")

        input_type = st.radio(
            "Select Input Type:",
            ("Image", "Video", "Live Camera")
        )

        # IMAGE
        if input_type == "Image":
            image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

            if image is not None:
                file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, 1)

                results = model(img)
                annotated = results[0].plot()

                st.image(annotated, use_container_width=True)

        # VIDEO
        elif input_type == "Video":
            video = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])

            if video is not None:
                st.video(video)
                st.warning("Video processing will be added soon 🚀")

        # LIVE CAMERA
        elif input_type == "Live Camera":

            from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

            class YOLOCamera(VideoTransformerBase):
                def __init__(self):
                    self.model = model

                def transform(self, frame):
                    img = frame.to_ndarray(format="bgr24")
                    results = self.model(img)
                    return results[0].plot()

            webrtc_streamer(
                key="yolo-live",
                video_transformer_factory=YOLOCamera,
                media_stream_constraints={"video": True, "audio": False}
            )

    # ================= ANALYTICS =================
    elif menu == "Analytics":
        st.title("📊 Analytics Dashboard")
        st.write("Graphs and statistics will be shown here")

    # ================= SETTINGS =================
    elif menu == "Settings":
        st.title("⚙️ Settings")
        st.write("User preferences and system settings")
