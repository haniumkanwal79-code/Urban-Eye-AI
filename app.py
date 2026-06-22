import streamlit as st
from supabase import create_client, Client
from streamlit_cookies_controller import CookieController
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

SUPABASE_URL = "https://mrwkglukekmikenihkfp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yd2tnbHVrZWttaWtlbmloa2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDQwODgsImV4cCI6MjA5NzcyMDA4OH0.Y1UpomD34O8shloIV6OGVFET5BFVfawLk2yDJZQy8yM"

# Client aur Cookie Controller initialize karein
if "supabase_client" not in st.session_state:
    st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = st.session_state.supabase_client
controller = CookieController()

if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================================
# 2. EMAIL SENDING LOGIC (BACKEND REVENUE)
# =====================================================================
def send_report_email(to_email, subject, body, attachment_path=None):
    sender_email = "your_email@gmail.com" 
    sender_password = "your_app_password_here" 

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

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
                
                # 🔥 Browser Cookie me access token save kar rahe hain
                if res.session:
                    controller.set("urban_eye_token", res.session.access_token)
                    
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
                st.info("📨 Signup successful! Aap ab direct login tab par jaakar login kar sakte hain.")
            except Exception as e:
                st.error(f"❌ Signup Failed: {e}")

# =====================================================================
# 4. CONTROL CONTROLLER (MAIN APP TRIGGER & ROUTING)
# =====================================================================
def main():
    # 🔥 Cookie se saved token nikalne ki koshish karein
    saved_token = controller.get("urban_eye_token")

    if st.session_state.user is None and saved_token:
        try:
            # Saved token ke zariye user data dobara fetch karein (Bypassing Login)
            user_res = supabase.auth.get_user(saved_token)
            if user_res and user_res.user:
                st.session_state.user = user_res.user
        except Exception:
            # Agar token expire ho chuka ho to cookie remove kar dein
            controller.remove("urban_eye_token")

    # Logout handler link ke liye (agar home.py se user login state clear kare)
    if st.session_state.user is None and not saved_token:
        show_auth_page()
    elif st.session_state.user is None and saved_token:
        # Recovery layer agar user update process me ho
        show_auth_page()
    else:
        # Ek check ke agar user home se manual logout dabaye to cookie uradni hai
        show_home()
        
        # Agar home.py chalne ke baad session state khali ho jaye (User clicked logout)
        if st.session_state.user is None:
            controller.remove("urban_eye_token")
            st.rerun()

if __name__ == "__main__":
    main()
