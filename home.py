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
    /* ================= SURVEILLANCE PREMIUM UI ================= */

.surv-title {
    font-size:34px;
    font-weight:900;
    color:#00e5ff;
    text-align:center;
    text-shadow:0px 0px 15px rgba(0,229,255,0.5);
    margin-bottom:10px;
}

.mode-box {
    background: rgba(15, 23, 42, 0.8);
    border:1px solid rgba(0,229,255,0.2);
    padding:12px;
    border-radius:12px;
    box-shadow:0px 0px 20px rgba(0,229,255,0.08);
}

.detect-box {
    background: linear-gradient(135deg,#0f172a,#111c33);
    border-left:4px solid #00ffcc;
    padding:12px;
    border-radius:10px;
    margin:6px 0px;
    color:white;
    transition:0.3s;
}

.detect-box:hover {
    transform:scale(1.02);
    box-shadow:0px 0px 15px rgba(0,255,204,0.2);
}

.video-frame {
    border-radius:15px;
    border:2px solid rgba(0,229,255,0.4);
    box-shadow:0px 0px 25px rgba(0,229,255,0.15);
}

.live-status {
    background: #1b1f36;
    border-left:5px solid red;
    padding:10px;
    border-radius:10px;
    color:white;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { box-shadow:0px 0px 5px red; }
    50% { box-shadow:0px 0px 20px red; }
    100% { box-shadow:0px 0px 5px red; }
}

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

   def upload_section():

    st.markdown('<div class="surv-title">📡 AI SURVEILLANCE COMMAND CENTER</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="live-status">
    🔴 REAL-TIME MONITORING ACTIVE | YOLO AI ENGINE RUNNING | GOVERNMENT NODE CONNECTED
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("Select Surveillance Mode", ["Image", "Video", "Live Camera"])

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

            st.markdown("### 🚨 DETECTED VIOLATIONS")

            for d in detected:
                st.markdown(f"""
                <div class="detect-box">🔴 {d}</div>
                """, unsafe_allow_html=True)

            if st.button("📄 Generate Government Report"):
                img_path = f"gov_report_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, img)

                for issue in detected:
                    generate_report(issue, location, img_path)

    # ================= VIDEO =================
    elif mode == "Video":

        st.markdown('<div class="mode-box">📹 VIDEO INTELLIGENCE MODE ACTIVE</div>', unsafe_allow_html=True)

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

                stframe.image(annotated, channels="BGR", use_container_width=True)

                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        name = model.names[cls]
                        if name.lower() != "person":
                            detected_all.append(name)

            cap.release()

            detected_all = list(set(detected_all))

            st.success(f"ANALYSIS COMPLETE ✔")

            for d in detected_all:
                st.markdown(f"<div class='detect-box'>⚠ {d}</div>", unsafe_allow_html=True)

    # ================= LIVE CAMERA =================
    elif mode == "Live Camera":

        st.markdown('<div class="live-status">🔴 LIVE FEED ACTIVE - HIGH SECURITY MODE</div>', unsafe_allow_html=True)

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

        if st.button("📸 CAPTURE & GENERATE REPORT"):

            if st.session_state.last_frame is not None:

                img_path = f"live_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(img_path, st.session_state.last_frame)

                for issue in st.session_state.last_detected:
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
# ================= ANALYTICS (MAX PREMIUM UPGRADE) =================
def analytics():

    st.markdown("""
    <style>
    .intel-header{
        font-size:32px;
        font-weight:900;
        color:#00e5ff;
        text-align:center;
        margin-bottom:10px;
    }

    .intel-sub{
        text-align:center;
        color:#9fb3c8;
        margin-bottom:25px;
    }

    .kpi-box{
        background: linear-gradient(135deg,#0f172a,#111c33);
        padding:20px;
        border-radius:16px;
        text-align:center;
        border:1px solid rgba(0,229,255,0.2);
        box-shadow:0px 0px 20px rgba(0,229,255,0.08);
    }

    .kpi-value{
        font-size:28px;
        font-weight:900;
        color:#00ffcc;
    }

    .kpi-label{
        color:#9fb3c8;
        font-size:14px;
    }

    .intel-box{
        background:#1b1f36;
        padding:15px;
        border-left:5px solid #00e5ff;
        border-radius:10px;
        color:white;
        margin-top:15px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="intel-header">📊 NATIONAL INTELLIGENCE ANALYTICS CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="intel-sub">Real-Time Urban Monitoring | Predictive Violation System | AI Insights Engine</div>', unsafe_allow_html=True)

    # ================= KPI CARDS =================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="kpi-box"><div class="kpi-value">1240</div><div class="kpi-label">Total Reports</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="kpi-box"><div class="kpi-value">78%</div><div class="kpi-label">Detection Accuracy</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="kpi-box"><div class="kpi-value">260</div><div class="kpi-label">Active Alerts</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="kpi-box"><div class="kpi-value">18</div><div class="kpi-label">Monitored Zones</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # ================= DATA =================
    df = pd.DataFrame({
        "Sector": ["Road", "Garbage", "Water", "Electricity", "Other"],
        "Reports": [320, 210, 400, 150, 160]
    })

    colA, colB = st.columns(2)

    with colA:
        st.subheader("📈 Sector Wise Reports Trend")
        st.line_chart(df.set_index("Sector"))
        st.bar_chart(df.set_index("Sector"))

    with colB:
        st.subheader("🔥 Risk Heatmap Simulation")

        heat_df = pd.DataFrame({
            "Zone A": [8, 3, 5],
            "Zone B": [6, 9, 2],
            "Zone C": [4, 7, 6]
        }, index=["Road", "Garbage", "Water"])

        st.dataframe(heat_df, use_container_width=True)

    # ================= AI INSIGHT ENGINE =================
    st.markdown("""
    <div class="intel-box">
    🧠 AI INSIGHT ENGINE:<br><br>
    • High violation density detected in ROAD sector (Urban highways)<br>
    • Garbage complaints increasing in Zone B (Possible waste management failure)<br>
    • Water-related issues stable but rising in outskirts<br>
    • Predictive Alert: Next 7 days → 12% increase in road violations expected
    </div>
    """, unsafe_allow_html=True)

    # ================= DOWNLOAD BUTTON =================
    report_df = df.copy()
    csv = report_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "⬇ Download Intelligence Report (CSV)",
        data=csv,
        file_name="national_intelligence_report.csv",
        mime="text/csv"
    )

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
