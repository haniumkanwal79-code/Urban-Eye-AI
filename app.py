import streamlit as st
from supabase import create_client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# =====================================================================
# 1. INITIALIZATION & CONNECTIONS
# =====================================================================
SUPABASE_URL = "https://mrwkglukekmikenihkfp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yd2tnbHVrZWttaWtlbmloa2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxNDQwODgsImV4cCI6MjA5NzcyMDA4OH0.Y1UpomD34O8shloIV6OGVFET5BFVfawLk2yDJZQy8yM"

if "supabase_client" not in st.session_state:
    try:
        st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Database Connection Error: {e}")

supabase = st.session_state.get("supabase_client", None)

if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================================
# 2. UPDATED EMAIL TRANSMISSION LOGIC
# =====================================================================
def send_report_email(to_email, subject, body, attachment_path=None):
    # Ab session state se credentials utha raha hai
    sender_email = st.session_state.get("user_email")
    sender_password = st.session_state.get("user_app_password")

    if not sender_email or not sender_password:
        st.error("Email credentials missing. Please re-login.")
        return False

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
        st.error(f"SMTP Error: {e}")
        return False

# =====================================================================
# 3. UI & AUTH PAGE
# =====================================================================
def show_auth_page():
    st.markdown("""<style>.block-container{padding-top:2.5rem;max-width:560px;}</style>""", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="premium-brand-card" style="background:#111827; padding:20px; border-radius:15px; text-align:center;">
            <h1 style="color:white;">URBAN EYE AI</h1>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✦ SIGN IN", "✦ CREATE ACCOUNT"])

    with tab1:
        email = st.text_input("Email Address", key="l_email")
        password = st.text_input("Password", type="password", key="l_password")
        # Naya Field: App Password
        app_password = st.text_input("Google App Password", type="password", 
                                     help="Gmail ke liye 'App Password' use karein. (Settings -> 2FA -> App Passwords)")
        
        if st.button("LOG IN TO SYSTEM", use_container_width=True):
            if not email or not app_password:
                st.warning("Email aur App Password dono zaroori hain!")
            else:
                with st.spinner("Authenticating..."):
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = res.user
                        # Credentials save karein
                        st.session_state.user_email = email
                        st.session_state.user_app_password = app_password
                        st.rerun()
                    except Exception:
                        st.error("Login failed. Check your credentials.")

    with tab2:
        s_email = st.text_input("Your Email Address", key="s_email")
        s_password = st.text_input("Choose a Password", type="password", key="s_password")
        if st.button("REGISTER ACCOUNT", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": s_email, "password": s_password})
                st.info("Registration successful! Please login.")
            except Exception as e:
                st.error(f"Error: {e}")

# =====================================================================
# 4. MAIN ROUTER
# =====================================================================
def main():
    if st.session_state.user is None:
        show_auth_page()
    else:
        st.success(f"Logged in as: {st.session_state.user.email}")
        if st.button("Log Out"):
            st.session_state.user = None
            st.session_state.user_email = None
            st.session_state.user_app_password = None
            st.rerun()

if __name__ == "__main__":
    main()
