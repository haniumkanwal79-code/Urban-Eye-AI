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


# ================= PREMIUM CSS (UPGRADED UI ONLY) =================
def load_css():
    st.markdown("""
    <style>

    /* GLOBAL */
    body {
        background: radial-gradient(circle at top, #0b1220, #050814);
    }

    /* TITLE */
    .gov-title {
        font-size:52px;
        font-weight:900;
        text-align:center;
        color:#00e5ff;
        letter-spacing:3px;
        text-shadow:0px 0px 20px rgba(0,229,255,0.6);
        margin-bottom:5px;
    }

    .gov-subtitle {
        text-align:center;
        color:#a9c4d8;
        margin-bottom:30px;
        font-size:17px;
    }

    /* GLASS CARD */
    .gov-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        padding:24px;
        border-radius:18px;
        box-shadow:0px 0px 25px rgba(0,229,255,0.10);
        color:white;
        text-align:center;
        border:1px solid rgba(0,229,255,0.2);
        transition:0.3s ease-in-out;
    }

    .gov-card:hover {
        transform: scale(1.05);
        box-shadow:0px 0px 35px rgba(0,229,255,0.35);
    }

    /* METRICS */
    .metric-big {
        font-size:34px;
        font-weight:900;
        color:#00ffcc;
        text-shadow:0px 0px 10px rgba(0,255,204,0.4);
    }

    /* ALERT BOX */
    .alert-box {
        background: linear-gradient(90deg, #0f172a, #111c33);
        border-left:5px solid #00e5ff;
        padding:14px;
        border-radius:12px;
        color:white;
        box-shadow:0px 0px 20px rgba(0,229,255,0.15);
    }

    /* BUTTONS */
    .stButton button {
        background: linear-gradient(90deg, #00e5ff, #00ffcc);
        color:black;
        font-weight:bold;
        border-radius:10px;
        border:none;
    }

    .stButton button:hover {
        transform: scale(1.05);
        box-shadow:0px 0px 15px rgba(0,255,204,0.5);
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1220, #050814);
    }

    </style>
    """, unsafe_allow_html=True)


# ================= REPORT SYSTEM =================
def generate_report(issue_type, location, image_path):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pdf_path = create_pdf(
        issue_type=issue_type,
        location=location,
        image_path=image_path,
        timestamp=timestamp
    )

    st.success("🏛 Official Government Report Generated")

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇ Download Official Report (Gov Format)",
            f,
            file_name="National_Urban_Report.pdf",
            mime="application/pdf"
        )


# ================= DASHBOARD =================
def dashboard():

    st.markdown('<div class="gov-title">🏛 NATIONAL URBAN INTELLIGENCE CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="gov-subtitle">Real-Time Smart City Monitoring & AI Enforcement System</div>', unsafe_allow_html=True)

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
    🧠 AI INSIGHT: High violation density detected in metropolitan highway zones (6PM - 11PM).
    </div>
    """, unsafe_allow_html=True)


# ================= DETECTION =================
def upload_section():

    st.title("📡 AI Surveillance & Detection Grid")

    mode = st.radio("Select Mode", ["Image", "Video", "Live Camera"])

    # ================= IMAGE =================
    if mode == "Image":

        image = st.file_uploader("Upload City Evidence Image", type=["jpg","png","jpeg"])
        location = st.text_input("📍 Location Tag", "Unknown Zone")

        if image:

            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            results = model.predict(img, conf=0.5)
            annotated = results[0].plot()

            st.image(annotated, caption="AI Detection Output", use_container_width=True)

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

            if st.button("📄 Generate Government Report"):
                img_path = f"gov_report_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, img)

                for issue in detected:
                    generate_report(issue, location, img_path)

    # ================= VIDEO =================
    elif mode == "Video":

        st.info("📡 Video Intelligence Mode Active")

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

            st.success(f"Analysis Completed ✔ | Issues: {detected_all}")

    # ================= LIVE CAMERA =================
    elif mode == "Live Camera":

        st.warning("🔴 LIVE SURVEILLANCE ACTIVE")

        location = st.text_input("📍 Location Tag", "Unknown Zone")

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
            key="gov-live",
            video_transformer_factory=GovCamera,
            media_stream_constraints={"video": True, "audio": False}
        )

        if st.button("📸 CAPTURE & REPORT"):

            if st.session_state.last_frame is not None:

                img_path = f"live_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, st.session_state.last_frame)

                for issue in st.session_state.last_detected:
                    generate_report(issue, location, img_path)


# ================= ANALYTICS =================
def analytics():

    st.title("📊 Analytics Dashboard")

    df = pd.DataFrame({
        "Sector": ["Road", "Garbage", "Water", "Electricity", "Other"],
        "Reports": [320, 210, 400, 150, 160]
    })

    st.bar_chart(df.set_index("Sector"))


# ================= SETTINGS =================
def settings():

    st.title("⚙️ Control Panel")

    st.checkbox("Enable AI Alerts")
    st.checkbox("Enable Logging")
    st.selectbox("Priority Level", ["Low", "Medium", "High", "Critical"])


# ================= MAIN =================
def show_home():

    load_css()

    menu = st.sidebar.radio(
        "🏛 CONTROL CENTER",
        ["🏛 Dashboard", "📡 Surveillance Grid", "📊 Analytics", "⚙️ Settings"]
    )

    st.sidebar.success("SYSTEM ACTIVE")
    st.sidebar.info("YOLOv8 AI Engine Running")

    if menu == "🏛 Dashboard":
        dashboard()
    elif menu == "📡 Surveillance Grid":
        upload_section()
    elif menu == "📊 Analytics":
        analytics()
    elif menu == "⚙️ Settings":
        settings()
