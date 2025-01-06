import streamlit as st
import functions.auth_functions as auth_functions
from PIL import Image

logo = Image.open("logo.ico")
st.set_page_config(
    page_title="Prosterio",
    page_icon=logo,
)

# -------------------------------------------------------------------------------------------------
# Not logged in
# -------------------------------------------------------------------------------------------------
if "user_info" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    st.navigation(
        [st.Page("./pages/demo.py", title="Prosterio")],
        position="hidden",
        expanded=False,
    )
    with col2:
        # Display logo and app description
        st.markdown(
            """
        <div style="display: flex; align-items: center; margin: 20px 0; justify-content: space-between;">
            <img src="https://raw.githubusercontent.com/ayusudi/prosterio/refs/heads/main/logo.png" alt="Logo" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover;">
            <div style="width:175px">
                <p style="font-weight:bold; font-size:32px; font-family: 'Nunito', sans-serif; margin: 0">Prosterio</p>
                <p style="font-size:15px; margin: 0; font-family: 'Nunito', sans-serif; color: gray;">Streamline Tech Talent </br>for Project Managers</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Authentication form layout
        do_you_have_an_account = col2.selectbox(
            label="Do you have Prosperio Account?",
            options=("Yes", "No", "Yes, but I forgot my password"),
        )
        auth_form = col2.form(key="Authentication form", clear_on_submit=False)
        email = auth_form.text_input(label="Email")
        password = (
            auth_form.text_input(label="Password", type="password")
            if do_you_have_an_account in {"Yes", "No"}
            else auth_form.empty()
        )
        auth_notification = col2.empty()

        # Sign In
        if do_you_have_an_account == "Yes" and auth_form.form_submit_button(
            label="Sign In", use_container_width=True, type="primary"
        ):
            with auth_notification, st.spinner("Signing in"):
                auth_functions.sign_in(email, password)

        # Create Account
        elif do_you_have_an_account == "No" and auth_form.form_submit_button(
            label="Create Account", use_container_width=True, type="primary"
        ):
            with auth_notification, st.spinner("Creating account"):
                auth_functions.create_account(email, password)

        # Password Reset
        elif (
            do_you_have_an_account == "Yes, but I forgot my password"
            and auth_form.form_submit_button(
                label="Send Password Reset Email",
                use_container_width=True,
                type="primary",
            )
        ):
            with auth_notification, st.spinner("Sending password reset link"):
                auth_functions.reset_password(email)

        # Authentication success and warning messages
        if "auth_success" in st.session_state:
            auth_notification.success(st.session_state.auth_success)
            del st.session_state.auth_success
        elif "auth_warning" in st.session_state:
            auth_notification.warning(st.session_state.auth_warning)
            del st.session_state.auth_warning

# -------------------------------------------------------------------------------------------------
# Logged in
# -------------------------------------------------------------------------------------------------
else:
    # Sidebar Navigation
    # Render the sidebar content at the top
    # st.sidebar._is_top_level = True

    # Define navigation pages
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://raw.githubusercontent.com/ayusudi/prosterio/refs/heads/main/sidebarlogo.png);
                background-size: 310px 150px;
                background-repeat: no-repeat;
                padding-top: 168px;
                background-position: 15px 0px;
                height: 210px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def logout():
        auth_functions.sign_out()
        st.session_state.pop("user_info", None)
        pg = st.navigation(
            [st.Page("./pages/demo.py", title="Video Demo")], position="hidden"
        )
        pg.run()
        st.rerun()

    dashboard_page = st.Page(
        "./pages/dashboard.py", title="Dashboard", icon=":material/dashboard:"
    )
    chat_page = st.Page("./pages/chat.py", title="PM Assistant", icon=":material/chat:")
    add_talent_page = st.Page(
        "./pages/add_talent.py", title="Add IT Talent", icon=":material/person_add:"
    )
    settings_page = st.Page(
        "./pages/settings.py", title="Settings", icon=":material/settings:"
    )
    logout = st.Page(logout, title="Log out", icon=":material/logout:")
    pg = st.navigation(
        [dashboard_page, chat_page, add_talent_page, settings_page, logout],
        position="sidebar",
        expanded=True,
    )
    pg.run()
