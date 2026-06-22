# =====================================================================
# 4. CONTROL CONTROLLER (MAIN APP TRIGGER) - FIXED FOR GOOGLE AUTH
# =====================================================================
def main():
    # 1. URL me se fragments ya query parameters check karein
    query_params = st.query_params
    
    # 2. Agar user pehle se state me nahi hai, to Supabase ke active session ko check karein
    if st.session_state.user is None:
        try:
            # Supabase built-in method browser cookies/session check karne ke liye
            user = supabase.auth.get_user()
            if user:
                st.session_state.user = user.user
                st.rerun()
        except Exception:
            # Agar koi active session nahi mila, to handle karein via query params
            if "access_token" in query_params:
                try:
                    # Token detect hone par user setup
                    st.session_state.user = supabase.auth.get_user(query_params["access_token"]).user
                    st.rerun()
                except:
                    pass

    # 3. Page Routing Logic
    if st.session_state.user is None:
        show_auth_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
