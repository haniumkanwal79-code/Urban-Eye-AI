elif input_type == "Live Camera":

    st.subheader("🎯 AI Detection Sensitivity")

    confidence = st.slider(
        "Model Sensitivity",
        0.10,
        1.00,
        0.50,
        0.05
    )

    class YOLOCamera(VideoTransformerBase):

        def __init__(self):
            self.model = model
            self.conf = confidence

        def transform(self, frame):

            img = frame.to_ndarray(format="bgr24")

            results = self.model.predict(
                img,
                conf=self.conf
            )

            annotated_frame = img.copy()

            person_detected = False

            for r in results:
                boxes = r.boxes

                for box in boxes:

                    cls_id = int(box.cls[0])
                    class_name = self.model.names[cls_id]

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # ================= PERSON FILTER =================
                    if class_name.lower() == "person":
                        person_detected = True
                        continue  # skip drawing person

                    # ================= DRAW ONLY URBAN ISSUES =================
                    cv2.rectangle(
                        annotated_frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        annotated_frame,
                        class_name,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

            # ================= WARNING IF PERSON DETECTED =================
            if person_detected:
                cv2.putText(
                    annotated_frame,
                    "PERSON DETECTED - URBAN FILTER ACTIVE",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            return annotated_frame

    webrtc_streamer(
        key="live",
        video_transformer_factory=YOLOCamera,
        media_stream_constraints={
            "video": True,
            "audio": False
        }
    )

    st.info(f"Current Sensitivity: {confidence}")
