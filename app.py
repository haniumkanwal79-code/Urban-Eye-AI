import streamlit as st
import home

st.set_page_config(
    page_title="Modern Login Page",
    page_icon="🔐",
    layout="centered"
)

# SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ROUTING
if st.session_state.logged_in:
    home.show_home()
    st.stop()

# ================= LOGIN UI =================
st.markdown("""
<style>
body { background-color: #0f172a; }

.stApp {
    background: linear-gradient(to right, #0f172a, #1e293b);
}

.login-box {
    background-color: white;
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.2);
}

.title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
    color: #2563eb;
}

.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 30px;
}

.stButton > button {
    width: 100%;
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    height: 45px;
    font-size: 18px;
}

.stButton > button:hover {
    background-color: #1d4ed8;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown('<div class="title">Welcome Back 👋</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Login to continue</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

    if username == "admin" and password == "1234":

        st.session_state.logged_in = True

        # FORCE REFRESH SAFE WAY
        st.success("Login Successful")

        st.switch_page  # fallback safe (if available)

        st.rerun()

    else:
        st.error("Invalid Credentials")
