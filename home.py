import streamlit as st
from ultralytics import YOLO
import numpy as np
import cv2

# Load YOLO Model
model = YOLO("best.pt")

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Urban Issue Reporter",
    page_icon="🚀",
    layout="wide"
)

# ================= SESSION STATE =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

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

# ================= CUSTOM CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b, #111827);
    color: white;
}

p, span, label, div {
    color: #ffffff !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

.main-title {
    font-size: 55px;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 10px;
}

.subtitle {
    font-size: 20px;
    color: #cbd5e1;
    margin-bottom: 40px;
}

.card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    padding: 30px;
    border-radius: 25px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.1);
}

.card:hover {
    transform: translateY(-8px);
}

.stButton > button {
    background: linear-gradient(to right, #38bdf8, #2563eb);
    color: white !important;
    border: none;
    border-radius: 12px;
    height: 50px;
    width: 180px;
    font-size: 18px;
    font-weight: 600;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 20px;
}

section[data-testid="stSidebar"] {
    background: #111827;
}

div[data-testid="stTextInput"] input {
    color: #111111 !important;
    background-color: white !important;
}
</style>
""", unsafe_allow_html=True)

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

    with m1:
        st.metric("Total Complaints", "1240")

    with m2:
        st.metric("Resolved", "980")

    with m3:
        st.metric("Pending", "260")

# ================= UPLOAD ISSUE PAGE =================
elif menu == "Upload Issue":

    st.title("📥 Upload Issue")
    st.write("Upload image, video or use live camera.")

    input_type = st.radio(
        "Select Input Type",
        ["Image", "Video", "Live Camera"]
    )

    # IMAGE
    if input_type == "Image":

        image = st.file_uploader(
            "Upload Image",
            type=["jpg", "jpeg", "png"]
        )

        if image is not None:

            file_bytes = np.asarray(
                bytearray(image.read()),
                dtype=np.uint8
            )

            img = cv2.imdecode(file_bytes, 1)

            results = model(img)

            annotated = results[0].plot()

            st.image(
                annotated,
                caption="Detected Image",
                use_container_width=True
            )

    # VIDEO
    elif input_type == "Video":

        video = st.file_uploader(
            "Upload Video",
            type=["mp4", "avi", "mov"]
        )

        if video is not None:
            st.video(video)
            st.warning(
                "Video detection will be added in next version."
            )

    # LIVE CAMERA
    elif input_type == "Live Camera":

        from streamlit_webrtc import (
            webrtc_streamer,
            VideoTransformerBase
        )

        class YOLOCamera(VideoTransformerBase):

            def __init__(self):
                self.model = model

            def transform(self, frame):

                img = frame.to_ndarray(
                    format="bgr24"
                )

                results = self.model(img)

                return results[0].plot()

        webrtc_streamer(
            key="yolo-live",
            video_transformer_factory=YOLOCamera,
            media_stream_constraints={
                "video": True,
                "audio": False
            }
        )

# ================= ANALYTICS PAGE =================
elif menu == "Analytics":

    st.title("📊 Analytics Dashboard")
    st.write("Graphs and statistics will be shown here.")

# ================= SETTINGS PAGE =================
elif menu == "Settings":

    st.title("⚙️ Settings")
    st.write("User preferences and system settings.")
