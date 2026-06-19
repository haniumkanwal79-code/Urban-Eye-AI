import streamlit as st
from ultralytics import YOLO
import numpy as np
import cv2
import pandas as pd
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from pdf_utils import create_pdf
import os

# ================= SAFE GPS (NO EXTRA LIB REQUIRED) =================
def get_location():
    location = st.text_input("📍 Enter your location (auto GPS optional)", "Unknown")
    return location


# ================= PDF SYSTEM =================
def generate_report(issue_type, location, image_path):

    pdf_path = create_pdf(issue_type, location, image_path)

    st.success("📄 PDF Generated")

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇ Download Report",
            f,
            file_name="report.pdf",
            mime="application/pdf"
        )


# ================= MAIN =================
def show_home():

    model = YOLO("best.pt")

    if "menu" not in st.session_state:
        st.session_state.menu = "🏠 Home"

    menu = st.sidebar.radio(
        "Menu",
        ["🏠 Home", "📥 Upload Issue", "📊 Analytics", "⚙️ Settings"]
    )

    # ================= HOME =================
    if menu == "🏠 Home":
        st.title("Urban AI Dashboard")

    # ================= UPLOAD =================
    elif menu == "📥 Upload Issue":

        st.title("Upload Issue")

        input_type = st.radio("Input", ["Image", "Video", "Live Camera"])

        # ================= IMAGE =================
        if input_type == "Image":

            image = st.file_uploader("Upload Image", type=["jpg","png"])
            location = get_location()

            if image:

                file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, 1)

                results = model.predict(img, conf=0.5)
                annotated = results[0].plot()

                st.image(annotated)

                if st.button("Generate Report"):

                    for r in results:
                        for box in r.boxes:

                            cls_id = int(box.cls[0])
                            class_name = model.names[cls_id]

                            if class_name.lower() == "person":
                                continue

                            img_path = f"report_{class_name}.jpg"
                            cv2.imwrite(img_path, img)

                            generate_report(class_name, location, img_path)

        # ================= LIVE =================
        elif input_type == "Live Camera":

            st.warning("Live GPS auto not supported in Streamlit Web safely")
            location = get_location()

            st.info(f"Location: {location}")

    # ================= OTHER =================
    elif menu == "📊 Analytics":
        st.bar_chart(pd.DataFrame({
            "Category": ["Road","Garbage"],
            "Count": [10,20]
        }))


    elif menu == "⚙️ Settings":
        st.checkbox("Enable Notifications")
