import streamlit as st
from ultralytics import YOLO
import numpy as np
import cv2
import pandas as pd
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ================= MODEL =================
model = YOLO("best.pt")

# ================= SESSION INIT =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "menu" not in st.session_state:
    st.session_state.menu = "Home"

# ================= ADVANCED SIDEBAR =================
st.sidebar.title("🚀 Urban Issue Reporter")

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "📌 Navigation",
    ["🏠 Home", "📥 Upload Issue", "📊 Analytics", "⚙️ Settings"],
    index=["🏠 Home", "📥 Upload Issue", "📊 Analytics", "⚙️ Settings"].index(
        st.session_state.menu if st.session_state.menu in 
        ["🏠 Home", "📥 Upload Issue", "📊 Analytics", "⚙️ Settings"] else "🏠 Home"
    )
)

# store selection
st.session_state.menu = menu

# logout button
st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ================= HOME =================
if menu == "🏠 Home":

    st.markdown("## 🚀 Urban Issue Reporter Dashboard")
    st.write("Welcome to AI-based urban issue detection system")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📍 Reports Module")

    with col2:
        st.success("🤖 AI Detection")

    with col3:
        st.warning("📊 Analytics")

    st.markdown("---")

    st.metric("Total Complaints", "1240")
    st.metric("Resolved", "980")
    st.metric("Pending", "260")

# ================= UPLOAD =================
elif menu == "📥 Upload Issue":

    st.title("📥 Upload Issue")

    input_type = st.radio(
        "Select Input Type:",
        ["Image", "Video", "Live Camera"]
    )

    # -------- IMAGE --------
    if input_type == "Image":

        image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

        if image is not None:
            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            results = model(img)
            annotated = results[0].plot()

            st.image(annotated, use_container_width=True)

    # -------- VIDEO --------
    elif input_type == "Video":

        video = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])

        if video is not None:
            st.video(video)
            st.warning("Video processing pipeline coming soon 🚀")

    # -------- LIVE CAMERA --------
    elif input_type == "Live Camera":

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
elif menu == "📊 Analytics":

    st.title("📊 Analytics Dashboard")

    st.subheader("Complaint Overview")

    data = {
        "Category": ["Road", "Garbage", "Street Light", "Water", "Other"],
        "Count": [320, 210, 150, 400, 160]
    }

    df = pd.DataFrame(data)
    st.bar_chart(df.set_index("Category"))

    st.subheader("Status Distribution")

    status = {
        "Status": ["Resolved", "Pending", "In Progress"],
        "Count": [980, 260, 120]
    }

    df2 = pd.DataFrame(status)
    st.bar_chart(df2.set_index("Status"))

    st.success("Live analytics system (demo data)")

# ================= SETTINGS =================
elif menu == "⚙️ Settings":

    st.title("⚙️ Settings")
    st.write("User preferences and configuration panel")

    st.checkbox("Enable Notifications")
    st.checkbox("Dark Mode (UI only demo)")
    st.selectbox("Report Priority Default", ["Low", "Medium", "High"])
