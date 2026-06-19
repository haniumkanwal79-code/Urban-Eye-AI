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

# ================= PREMIUM CSS (GOV STYLE UI) =================
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

    .status-bar {
        background:#0f172a;
        padding:10px;
        border-radius:10px;
        border:1px solid #1f2a44;
        color:#9fb3c8;
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


# ================= GOVERNMENT DASHBOARD =================
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
    Enforcement units recommended for deployment.
    </div>
    """, unsafe_allow_html=True)


# ================= DETECTION SYSTEM =================
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

            st.markdown("### 🚨 Violation Reported Objects")
            for d in detected:
                st.write("🔴", d)

            if st.button("📄 Generate Government Report"):

                img_path = f"gov_report_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, img)

                for issue in detected:
                    generate_report(issue, location, img_path)

    # ================= VIDEO =================
    elif mode == "Video":
        st.info("📡 Video intelligence module under government upgrade phase")

    # ================= LIVE CAMERA (ULTRA FIXED) =================
    elif mode == "Live Camera":

        st.warning("🔴 LIVE NATIONAL SURVEILLANCE ACTIVE")

        location = st.text_input("📍 Location Tag", "Unknown Zone")

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
                        cv2.putText(img, name, (x1,y1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                    (0,255,255), 2)

                if len(detected) > 0:
                    st.session_state.last_frame = img.copy()
                    st.session_state.last_detected = list(set(detected))

                return img

        webrtc_streamer(
            key="gov-live",
            video_transformer_factory=GovCamera,
            media_stream_constraints={"video": True, "audio": False}
        )

        if st.button("📸 CAPTURE & ISSUE GOVERNMENT REPORT"):

            if "last_frame" in st.session_state:

                img_path = f"gov_live_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, st.session_state.last_frame)

                for issue in st.session_state.last_detected:
                    generate_report(issue, location, img_path)

                st.success("🏛 Official Report Issued from Live Surveillance")


# ================= ANALYTICS =================
def analytics():

    st.title("📊 National Intelligence Analytics")

    df = pd.DataFrame({
        "Sector": ["Road", "Garbage", "Water", "Electricity", "Other"],
        "Reports": [320, 210, 400, 150, 160]
    })

    st.bar_chart(df.set_index("Sector"))

    st.success("📊 AI Trend: Infrastructure issues rising in urban core zones")


# ================= SETTINGS =================
def settings():

    st.title("⚙️ Government Control Panel")

    st.checkbox("Enable National AI Alerts")
    st.checkbox("Enable Surveillance Logging")
    st.checkbox("Dark Government Mode")
    st.selectbox("Priority Enforcement Level", ["Low", "Medium", "High", "Critical"])


# ================= MAIN APP =================
def show_home():

    load_css()

    menu = st.sidebar.radio(
        "🏛 National Control Menu",
        ["🏛 Dashboard", "📡 Surveillance Grid", "📊 Analytics", "⚙️ Settings"]
    )

    st.sidebar.markdown("### 🟢 SYSTEM STATUS: ACTIVE")
    st.sidebar.info("AI MODEL: YOLOv8 GOV EDITION")

    if menu == "🏛 Dashboard":
        dashboard()

    elif menu == "📡 Surveillance Grid":
        upload_section()

    elif menu == "📊 Analytics":
        analytics()

    elif menu == "⚙️ Settings":
        settings()
