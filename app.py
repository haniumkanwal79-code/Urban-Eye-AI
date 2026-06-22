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

SUPABASE_URL = "https://mrwkglukekmikenihkfp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yd2tnbHVrZWttaWtlbmloa2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDQwODgsImV4cCI6MjA5NzcyMDA4OH0.Y1UpomD34O8shloIV6OGVFET5BFVfawLk2yDJZQy8yM"

if "supabase_client" not in st.session_state:
    st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = st.session_state.supabase_client

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
    
    # 🔥 Checkbox ko Tabs se bahar nikal diya hai taake yeh 100% hamesha nazar aaye
    keep_logged_in = st.checkbox("🔄 Keep me logged in", value=True, key="remember_me")
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    # Email/Password Login
    with tab1:
        email = st.text_input("Email Address", key="l_email")
        password = st.text_input("Password", type="password", key="l_password")
        
        if st.button("Log In", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                
                # Agar main checkbox checked hai to URL me save karein
                if keep_logged_in:
                    st.query_params["session_user"] = email
                else:
                    st.query_params.clear()
                
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
    url_params = st.query_params.to_dict()
    
    # Background Auto-Login Layer
    if "session_user" in url_params and st.session_state.user is None:
        class DummyUser:
            def __init__(self, email):
                self.email = email
        st.session_state.user = DummyUser(url_params["session_user"])

    # Routing Logic
    if st.session_state.user is None:
        show_auth_page()
    else:
        # Main Dashboard running panel
        show_home()
        
        # Logout catch engine
        if st.session_state.user is None:
            st.query_params.clear() 
            st.rerun()

if __name__ == "__main__":
    main()
