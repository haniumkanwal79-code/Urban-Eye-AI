
import streamlit as st
from ultralytics import YOLO
import numpy as np
import cv2

model = YOLO("best.pt")

def show_home():

    # Page Config (ONLY ONCE, INSIDE FUNCTION)
    st.set_page_config(
        page_title="Modern Dashboard",
        page_icon="🚀",
        layout="wide"
    )

    st.write("HOME PAGE LOADED")

    # Logout Button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Sidebar Navigation
    st.sidebar.title("🚀 Navigation")

    menu = st.sidebar.radio(
        "Go to:",
        ["Home", "Upload Issue", "Analytics", "Settings"]
    )

    # ================= HOME =================
    if menu == "Home":
        st.title("🏠 Dashboard")
        st.write("Welcome to Home Page 🚀")

    # ================= UPLOAD =================
    elif menu == "Upload Issue":
        st.title("📥 Upload Issue")
        st.write("Upload image/video/live camera")

    # ================= ANALYTICS =================
    elif menu == "Analytics":
        st.title("📊 Analytics Dashboard")

    # ================= SETTINGS =================
    elif menu == "Settings":
        st.title("⚙️ Settings")

# Custom CSS
st.markdown("""
<style>
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Main Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b, #111827);
    color: white;
}

/* FORCE ALL TEXT WHITE */
p, span, label, div {
    color: #ffffff !important;
}

/* Remove Streamlit default spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* Main Heading */
.main-title {
    font-size: 55px;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    font-size: 20px;
    color: #cbd5e1;
    margin-bottom: 40px;
}

/* Stylish Cards */
.card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    padding: 30px;
    border-radius: 25px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
    transition: 0.3s;
    border: 1px solid rgba(255,255,255,0.1);
}

.card:hover {
    transform: translateY(-8px);
    box-shadow: 0px 12px 35px rgba(56,189,248,0.3);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(to right, #38bdf8, #2563eb);
    color: white !important;
    border: none;
    border-radius: 12px;
    height: 50px;
    width: 180px;
    font-size: 18px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
    background: linear-gradient(to right, #2563eb, #38bdf8);
}

/* Metric Styling */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Input Fix */
div[data-testid="stTextInput"] input {
    color: #111111 !important;
    background-color: rgba(255,255,255,0.95) !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 10px !important;
}

div[data-testid="stRadio"] label {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ================= HOME PAGE =================
if menu == "Home":
    # Header
    st.markdown(
        '<div class="main-title">🚀 Urban Issue Reporter</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Smart AI-Based Complaint & Monitoring System</div>',
        unsafe_allow_html=True
    )

    # Cards
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

    # Metrics
    st.write("")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Complaints", "1,240")
    m2.metric("Resolved", "980")
    m3.metric("Pending", "260")
    st.write("")

# ================= UPLOAD ISSUE PAGE =================
elif menu == "Upload Issue":
    st.title("📥 Upload Issue")
    st.write("Here user can upload image/video/live camera input")

    # Upload Section
    st.markdown("## 📥 Upload or Capture Input")
    input_type = st.radio(
        "Select Input Type:",
        ("Image", "Video", "Live Camera")
    )

    # ================= IMAGE =================
    if input_type == "Image":
        image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        if image is not None:
            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            results = model(img)
            annotated = results[0].plot()
            st.image(annotated, caption="Detected Image", use_container_width=True)

    # ================= VIDEO =================
    elif input_type == "Video":
        video = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
        if video is not None:
            st.video(video)
            st.warning("Video detection will be added in next upgrade 🚀")

    # ================= LIVE CAMERA =================
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

    st.write("")
    st.button("View Reports")

# ================= ANALYTICS PAGE =================
elif menu == "Analytics":
    st.title("📊 Analytics Dashboard")
    st.write("Graphs and statistics will be shown here")

# ================= SETTINGS PAGE =================
elif menu == "Settings":
    st.title("⚙️ Settings")
    st.write("User preferences and system settings")
