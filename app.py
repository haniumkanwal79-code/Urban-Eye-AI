import streamlit as st
from supabase import create_client, Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# 🟢 home.py se exact control center panel function ko import karna safely
try:
    from home import show_home
except ImportError:
    st.error("❌ 'home.py' file nahi mili! Kindly check karein ke dono files aik hi folder me hain.")

# =====================================================================
# 1. CONFIGURATION & CONNECTIONS
# =====================================================================

# Aapka Live Supabase Project Data
SUPABASE_URL = "https://mrwkglukekmikenihkfp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yd2tnbHVrZWttaWtlbmloa2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDQwODgsImV4cCI6MjA5NzcyMDA4OH0.Y1UpomD34O8shloIV6OGVFET5BFVfawLk2yDJZQy8yM"

# Client initialize karein
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Session State Initialize karein login state barkrar rakhne ke liye
if "user" not in st.session_state:
    st.session_state.user = None

# Streamlit Cloud par redirection ke liye live app ka link
def get_current_url():
    return "https://urban-eye-ai.streamlit.app"

# =====================================================================
# 2. EMAIL SENDING LOGIC (BACKEND REVENUE)
# =====================================================================
def send_report_email(to_email, subject, body, attachment_path=None):
    # ⚠️ IMPORTANT: Apna actual Gmail aur Google App Password yahan lagayein
    sender_email = "your_email@gmail.com" 
    sender_password = "your_app_password_here" 

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attachment logic
    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        msg.attach(part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

# =====================================================================
# 3. PAGES & UI (FRONTEND AUTHENTICATION)
# =====================================================================

# --- AUTHENTICATION SCREEN ---
def show_auth_page():
    st.subheader("🔐 Access Portal")
    st.caption("Please login or sign up to access the Urban Issue Detection System.")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    # Email/Password Login
    with tab1:
        email = st.text_input("Email Address", key="l_email")
        password = st.text_input("Password", type="password", key="l_password")
        if st.button("Log In", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.success("✅ Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Login Failed: {e}")

    # Email/Password Signup
    with tab2:
        s_email = st.text_input("Email Address", key="s_email")
        s_password = st.text_input("Password", type="password", key="s_password")
        if st.button("Create Account", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": s_email, "password": s_password})
                st.info("📨 Signup successful! Please check your email inbox to confirm your account.")
            except Exception as e:
                st.error(f"❌ Signup Failed: {e}")

    st.markdown("---")
    st.write("### Quick Access")
    
    # Google OAuth Button
    if st.button("🔴 Sign in with Google", use_container_width=True):
        try:
            redirect_uri = get_current_url()
            data = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {"redirect_to": redirect_uri} 
            })
            if data and data.url:
                st.markdown(f'<meta http-equiv="refresh" content="0; url={data.url}">', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Google OAuth Error: {e}")

# =====================================================================
# 4. CONTROL CONTROLLER (MAIN APP TRIGGER & ROUTING)
# =====================================================================
def main():
    # Safely user session cache se restore karne ki koshish karein
    if st.session_state.user is None:
        try:
            active_user = supabase.auth.get_user()
            if active_user and hasattr(active_user, 'user') and active_user.user:
                st.session_state.user = active_user.user
                st.rerun()
        except Exception:
            # URL Parameters se safely token nikalne ke liye inside try-except
            try:
                current_params = st.query_params.to_dict()
                if "access_token" in current_params:
                    token = current_params["access_token"]
                    st.session_state.user = supabase.auth.get_user(token).user
                    st.rerun()
            except Exception:
                pass

    # Routing Logic: Agar login nahi hai to auth screen, warna home.py ka dashboard
    if st.session_state.user is None:
        show_auth_page()
    else:
        # 🟢 Successfully login par home.py ka real YOLO surveillance center load hoga
        show_home()

if __name__ == "__main__":
    main()
