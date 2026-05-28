import streamlit as st
import av
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from ultralytics import YOLO

model = YOLO("best.pt")


class YOLOCamera(VideoTransformerBase):
    def __init__(self):
        self.model = model

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        results = self.model(img, conf=0.5)
        annotated = results[0].plot()
        return annotated


def show_home():

    st.title("📷 Live Camera Detection")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    use_camera = st.checkbox("Enable Live Camera")

    if use_camera:
        webrtc_streamer(
            key="live-camera",
            video_transformer_factory=YOLOCamera,
            media_stream_constraints={"video": True, "audio": False}
        )
