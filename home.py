# ================= DETECTION =================
def upload_section():
    st.title("📡 AI Surveillance & Detection Grid")
    mode = st.radio("Select Mode", ["Image", "Video", "Live Camera"])

    if mode == "Image":
        image = st.file_uploader("Upload City Evidence Image", type=["jpg","png","jpeg"])
        location = st.text_input("📍 Location Tag", "Unknown Zone")

        if image:
            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)

            if model:
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
            else:
                st.error("AI Model File ('best.pt') missing or failed to initialize.")

    elif mode == "Video":
        st.info("📡 Video Intelligence Mode Active")
        video_file = st.file_uploader("Upload Video", type=["mp4","avi","mov"])
        location = st.text_input("📍 Location Tag", "Video Surveillance Zone")

        if video_file and model:
            temp_path = "temp_video.mp4"
            with open(temp_path, "wb") as f:
                f.write(video_file.read())

            cap = cv2.VideoCapture(temp_path)
            detected_all = []
            stframe = st.empty()
            last_valid_frame = None

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = model.predict(frame, conf=0.5)
                annotated = results[0].plot()
                stframe.image(annotated, channels="BGR")

                frame_has_issue = False
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        name = model.names[cls]
                        if name.lower() != "person":
                            detected_all.append(name)
                            frame_has_issue = True
                
                if frame_has_issue:
                    last_valid_frame = frame.copy()

            cap.release()
            detected_all = list(set(detected_all))
            
            st.success(f"🎥 Video Processing Completed ✔ | Detected Issues: {detected_all}")
            
            if detected_all:
                if last_valid_frame is not None:
                    evidence_path = f"video_evidence_{datetime.now().timestamp()}.jpg"
                    cv2.imwrite(evidence_path, last_valid_frame)
                else:
                    evidence_path = None
                
                st.markdown("### 📋 Dispatch & Reporting Hub")
                if st.button("🚀 Process & Dispatch All Video Incident Reports"):
                    for issue in detected_all:
                        generate_report(issue, location, evidence_path)
            else:
                st.info("No urban hazards/issues flagged in this footage.")

    elif mode == "Live Camera":
        st.warning("🔴 LIVE SURVEILLANCE ACTIVE")
        location = st.text_input("📍 Location Tag", "Live Active Zone")

        # Session state variables freeze/lock logic ke liye
        if "frozen_frame" not in st.session_state:
            st.session_state.frozen_frame = None
        if "frozen_issues" not in st.session_state:
            st.session_state.frozen_issues = []

        # Yeh class handle karegi live detections ko background mein save karne ke liye
        class GovCamera(VideoTransformerBase):
            def transform(self, frame):
                img = frame.to_ndarray(format="bgr24")
                if model:
                    results = model.predict(img, conf=0.5, verbose=False)
                    detected = []

                    for r in results:
                        for box in r.boxes:
                            cls = int(box.cls[0])
                            name = model.names[cls]
                            if name.lower() != "person":
                                detected.append(name)
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,255), 2)
                            cv2.putText(img, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

                    # Har aane wale frame ko temporary stream buffer state me save rakhein
                    st.session_state.temp_live_frame = img.copy()
                    st.session_state.temp_live_detected = list(set(detected))
                return img

        # WebRTC component render karein
        webrtc_streamer(
            key="gov-live",
            video_transformer_factory=GovCamera,
            media_stream_constraints={"video": True, "audio": False}
        )

        st.markdown("---")
        
        # UI Columns Controls ke liye
        col_ctrl1, col_ctrl2 = st.columns(2)
        
        with col_ctrl1:
            if st.button("⏸️ FREEZE CURRENT FRAME", use_container_width=True):
                if "temp_live_frame" in st.session_state and st.session_state.temp_live_frame is not None:
                    st.session_state.frozen_frame = st.session_state.temp_live_frame.copy()
                    st.session_state.frozen_issues = st.session_state.temp_live_detected
                    st.toast("📸 Frame successfully locked & frozen!", icon="🎯")
                else:
                    st.error("Pehle camera start karein taake frame capture ho sake.")
        
        with col_ctrl2:
            if st.button("🔄 CLEAR FROZEN BUFFER", use_container_width=True):
                st.session_state.frozen_frame = None
                st.session_state.frozen_issues = []
                st.rerun()

        # Agar frame freeze ho chuka hai, to use display karein aur report option dein
        if st.session_state.frozen_frame is not None:
            st.markdown("### 🎯 Frozen Evidence Frame")
            
            # Frozen image ko web page par dikhayein conversion ke baad (BGR to RGB Streamlit ke liye)
            rgb_frozen = cv2.cvtColor(st.session_state.frozen_frame, cv2.COLOR_BGR2RGB)
            st.image(rgb_frozen, caption="Frozen Frame for Compliance Review", use_container_width=True)
            
            st.info(f"📋 **Detected Hazards in this locked frame:** {st.session_state.frozen_issues if st.session_state.frozen_issues else 'None'}")
            
            if st.session_state.frozen_issues:
                if st.button("📄 SEND REPORT FOR THIS FROZEN FRAME", use_container_width=True):
                    # Lock frame ko temporary disk space par save karein reports pipeline ke liye
                    frozen_path = f"frozen_live_{int(time.time())}.jpg"
                    cv2.imwrite(frozen_path, st.session_state.frozen_frame)
                    
                    # Sirf unhi issues ki report bhejein jo freeze ke waqt detect hue the
                    for issue in st.session_state.frozen_issues:
                        generate_report(issue, location, frozen_path)
            else:
                st.warning("Is frozen frame mein koi hazard maujood nahi hai. Dobara sahi frame par Freeze click karein.")
