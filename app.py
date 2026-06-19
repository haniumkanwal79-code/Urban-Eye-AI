import streamlit as st
import database as db
import os

# ================= EXTRA IMPORTS (REPORT SYSTEM) =================
from pdf_utils import create_pdf
from email_utils import send_email

# ================= DATABASE INIT =================
db.create_table()

os.makedirs("reports", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

st.write("DB exists:", os.path.exists("issues.db"))

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ================= AUTH FUNCTIONS =================
def signup_user(username, password):

    try:
        conn = db.get_connection()
        c = conn.cursor()

        c.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, password))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        st.error(f"Signup Error: {e}")
        return False


def login_user(username, password):

    try:
        conn = db.get_connection()
        c = conn.cursor()

        c.execute("""
            SELECT * FROM users
            WHERE username = ? AND password = ?
        """, (username, password))

        user = c.fetchone()

        conn.close()

        return user

    except Exception as e:
        st.error(f"Database Error: {e}")
        return None


# ================= 🚨 REPORT SYSTEM (PDF + EMAIL) =================
def generate_report(issue_type, location, image_path):

    # 1. CREATE PDF
    pdf_path = create_pdf(issue_type, location, image_path)

    # 2. EMAIL BODY
    subject = f"🚨 Urban Issue Detected: {issue_type}"

    body = f"""
    New Urban Issue Detected 🚨

    Issue Type: {issue_type}
    Location: {location}

    Please check attached PDF report.
    """

    # 3. SEND EMAIL WITH PDF
    send_email(subject, body, pdf_path)


# ================= ROUTING =================
if st.session_state.logged_in:

    import home
    home.show_home()
    st.stop()


# ================= LOGIN UI =================
st.title("🚀 Urban Issue Reporter AI System")

st.markdown("### Smart City AI Detection + Auto Reporting System")

menu = st.radio(
    "Choose Action",
    ["Login", "Sign Up"],
    horizontal=True
)


# ================= SIGN UP =================
if menu == "Sign Up":

    st.subheader("Create New Account")

    new_user = st.text_input("Create Username", key="signup_user")
    new_pass = st.text_input("Create Password", type="password", key="signup_pass")

    if st.button("Create Account"):

        if not new_user.strip():
            st.warning("Enter username")
        elif not new_pass.strip():
            st.warning("Enter password")
        else:

            if signup_user(new_user.strip(), new_pass.strip()):
                st.success("Account created successfully 🚀")


# ================= LOGIN =================
elif menu == "Login":

    st.subheader("Login")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):

        user = login_user(username.strip(), password.strip())

        if user:

            st.session_state.logged_in = True
            st.session_state.user = username

            st.success("Login successful 🚀")
            st.rerun()

        else:
            st.error("Invalid username or password ❌")
