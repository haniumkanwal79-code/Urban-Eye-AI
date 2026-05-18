import av
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

class YOLOCamera(VideoTransformerBase):
    def __init__(self):
        self.model = model

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        results = self.model(img, conf=0.5)
        annotated = results[0].plot()
        return annotated


st.markdown("## 📷 Live Camera Detection")

use_camera = st.checkbox("Enable Live Camera")

if use_camera:
    webrtc_streamer(
        key="live-camera",
        video_transformer_factory=YOLOCamera,
        media_stream_constraints={"video": True, "audio": False}
    )
