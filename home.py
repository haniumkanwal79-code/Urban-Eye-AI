def upload_section():

    st.title("📡 AI Detection System")

    input_type = st.radio("Input Mode", ["Image", "Live Camera"])

    location = st.text_input("📍 Location", "Unknown")

    # ================= IMAGE =================
    if input_type == "Image":

        image = st.file_uploader("Upload Image")

        if image:

            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            results = model.predict(img, conf=0.5)
            st.image(results[0].plot(), use_container_width=True)

            issues = []

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    name = model.names[cls]
                    if name.lower() != "person":
                        issues.append(name)

            issues = list(set(issues))

            st.success("Detection Done")

            for i in issues:

                severity = "High" if i in ["fire", "accident"] else "Medium"

                if st.button(f"Generate Report: {i}"):

                    img_path = f"{i}.jpg"
                    cv2.imwrite(img_path, img)

                    generate_report(i, location, img_path, severity)

    # ================= LIVE CAMERA =================
    elif input_type == "Live Camera":

        st.warning("🔴 Live Camera Mode Active")

        class LiveCam(VideoTransformerBase):

            def __init__(self):
                self.last_time = 0

            def transform(self, frame):

                img = frame.to_ndarray(format="bgr24")

                results = model.predict(img, conf=0.5)

                for r in results:
                    for box in r.boxes:

                        cls = int(box.cls[0])
                        name = model.names[cls]

                        if name.lower() == "person":
                            continue

                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            img,
                            name,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2
                        )

                return img


        webrtc_streamer(
            key="live-camera",
            video_transformer_factory=LiveCam,
            media_stream_constraints={
                "video": True,
                "audio": False
            }
        )

        st.info("⚡ Live AI Detection Running (Real-time)")
