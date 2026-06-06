import streamlit as st
import database as db

db.create_table()

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# ================= AUTH FUNCTIONS =================
def signup_user(username, password):
    conn = db.get_connection()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = db.get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, password))
    user = c.fetchone()
    conn.close()

    return user

# ================= LOGIN / SIGNUP UI =================
st.title("🚀 Urban Issue Reporter")

menu = st.radio("Choose Action", ["Login", "Sign Up"])

# ================= SIGN UP =================
if menu == "Sign Up":

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Create Account"):

        if signup_user(new_user, new_pass):
            st.success("Account created successfully 🚀")
        else:
            st.error("Username already exists ❌")

# ================= LOGIN =================
elif menu == "Login":

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = login_user(username, password)

        if user:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success("Login successful 🚀")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

# ================= ROUTE TO HOME =================
if st.session_state.logged_in:
    import home
    home.show_home()
