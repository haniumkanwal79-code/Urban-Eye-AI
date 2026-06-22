elif mode == "Live Camera":
        st.warning("🔴 LIVE SURVEILLANCE ACTIVE")
        location = st.text_input("📍 Location Tag", "Unknown Zone")

        # Session state variables ko initialize karein
        if "last_detected" not in st.session_state:
            st.session_state.last_detected = []

        # Simple callback function jo sirf object detection dikhane ke liye use hogi
        def video_frame_callback(frame):
            img = frame.to_ndarray(format="bgr24")
            
            if model:
                results = model.predict(img, conf=0.5)
                detected = []
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        name = model.names[cls]
                        if name.lower() != "person":
                            detected.append(name)
                        
                        # Bounding boxes draw karein live screen par
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
                
                # Global state ko update karne ke bajaye, hum detections ko read_video_frame mein process karenge
            return frame.from_ndarray(img, format="bgr24")

        # WebRTC Streamer context ko variable mein save karein
        ctx = webrtc_streamer(
            key="gov-live",
            video_frame_callback=video_frame_callback,
            media_stream_constraints={"video": True, "audio": False},
            desired_playing_state=True # Auto start live feed
        )

        st.markdown("---")
        st.markdown("### 📸 Live Reporting Trigger")

        # Jab button press hoga, ye live feed se current frame capture karega
        if st.button("📸 CAPTURE & REPORT CURRENT FRAME", use_container_width=True):
            if ctx.video_receiver:
                try:
                    # WebRTC receiver se sabse latest frame pull karein
                    video_frame = ctx.video_receiver.get_frame()
                    img = video_frame.to_ndarray(format="bgr24")
                    
                    if img is not None:
                        st.info("🔄 Frame captured! Running final analysis...")
                        
                        # Frame par dubara model run karein taake confirmation ho sake
                        if model:
                            results = model.predict(img, conf=0.5)
                            detected = []
                            
                            for r in results:
                                for box in r.boxes:
                                    cls = int(box.cls[0])
                                    name = model.names[cls]
                                    if name.lower() != "person":
                                        detected.append(name)
                                    
                                    # Image par clear boxes draw karein report ke liye
                                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
                            
                            detected = list(set(detected))
                            
                            if detected:
                                # Image disk par save karein
                                img_path = f"live_{datetime.now().timestamp()}.jpg"
                                cv2.imwrite(img_path, img)
                                
                                st.success(f"⚠️ Hazards Detected: {detected}")
                                
                                # Har issue ke liye report generate aur email send karein
                                for issue in detected:
                                    generate_report(issue, location, img_path)
                            else:
                                st.warning("No issues/hazards detected in the captured frame. Report aborted.")
                        else:
                            st.error("Model not loaded properly.")
                except Exception as e:
                    st.error(f"Error capturing frame from video stream: {str(e)}")
            else:
                st.error("WebRTC stream is not active. Please start the camera first.")
