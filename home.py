import streamlit as st
from ultralytics import YOLO
import numpy as np
import cv2

model = YOLO("best.pt")

def show_home():

    st.sidebar.title("🚀 Navigation")

    menu = st.sidebar.radio(
        "Go to:",
        ["Home", "Upload Issue", "Analytics", "Settings"]
    )

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ================= HOME =================
    if menu == "Home":
        st.markdown("## 🚀 Urban Issue Reporter Dashboard")
        st.write("Welcome to AI based system")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("📍 Reports Module")

        with col2:
            st.success("🤖 AI Detection")

        with col3:
            st.warning("📊 Analytics")

        st.metric("Total Complaints", "1240")
        st.metric("Resolved", "980")
        st.metric("Pending", "260")

    # ================= UPLOAD =================
    elif menu == "Upload Issue":

        st.title("📥 Upload Issue")

        input_type = st.radio(
            "Select Input Type:",
            ["Image", "Video", "Live Camera"]
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
            video = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])

            if video is not None:
                st.video(video)
                st.warning("Video processing coming soon 🚀")

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
                key="live",
                video_transformer_factory=YOLOCamera,
                media_stream_constraints={"video": True, "audio": False}
            )

    # ================= ANALYTICS =================
    elif menu == "Analytics":
        st.title("📊 Analytics Dashboard")
        st.write("Graphs coming soon")

    # ================= SETTINGS =================
    elif menu == "Settings":
        st.title("⚙️ Settings")
        st.write("User preferences here")
