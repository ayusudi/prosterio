import streamlit as st
import functions.auth_functions as auth_functions
from PIL import Image
import os, json
from snowflake.core import Root 
from snowflake.snowpark.session import Session
from streamlit_cookies_manager import EncryptedCookieManager

# This should be on top of your script
# Initialize cookie manager only once using session state
cookies = EncryptedCookieManager(
    prefix="ktosiek/streamlit-cookies-manager/",
    # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    password=os.environ.get("COOKIES_PASSWORD", "My secret password"),
)
    

if not cookies.ready():
    st.stop()
    
    

session = Session.builder.configs(
    {
        "user": st.secrets["snowflake_user"],
        "password": st.secrets["snowflake_password"],
        "account": st.secrets["snowflake_account"],
        "role": "accountadmin",
        "warehouse": st.secrets["snowflake_warehouse"],
        "database": st.secrets["snowflake_database"],
        "schema": "public",
    }
).create()

root = Root(session)

# """
# Initialize the session state for cortex search service metadata. Query the available
# cortex search services from the Snowflake session and store their names and search
# columns in the session state.
# """
if "service_metadata" not in cookies or not cookies['service_metadata'] or cookies['service_metadata'] == '':
    services = session.sql("SHOW CORTEX SEARCH SERVICES;").collect()
    service_metadata = []
    if services:
        for s in services:
            svc_name = s["name"]
            svc_search_col = session.sql(
                f"DESC CORTEX SEARCH SERVICE {svc_name};"
            ).collect()[0]["search_column"]
            service_metadata.append(
                {"name": svc_name, "search_column": svc_search_col}
            )
    cookies['service_metadata'] = json.dumps(service_metadata)
    cookies.save()

    
# st.write("Current cookies:", cookies)
# value = st.text_input("New value for a cookie")
# if st.button("Change the cookie"):
#     cookies['a-cookie'] = value  # This will get saved on next rerun
#     if st.button("No really, change it now"):
#         cookies.save()  # Force saving the cookies now, without a rerun

# -------------------------------------------------------------------------------------------------
# Not logged in
# -------------------------------------------------------------------------------------------------
if "user_info" not in cookies or cookies['user_info'] == "":
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
                auth_functions.sign_in(email, password, cookies=cookies)

        # Create Account
        elif do_you_have_an_account == "No" and auth_form.form_submit_button(
            label="Create Account", use_container_width=True, type="primary"
        ):
            with auth_notification, st.spinner("Creating account"):
                auth_functions.create_account(email, password, cookie=cookies)

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
                auth_functions.reset_password(email, cookies)

        # Authentication success and warning messages
        if "auth_success" in cookies and cookies['auth_success'] != "":
            auth_notification.success(cookies['auth_success'])
            del cookies['auth_success']
        elif "auth_warning" in cookies and cookies['auth_warning']!= "":
            auth_notification.warning(cookies['auth_warning'])
            del cookies['auth_warning']

# -------------------------------------------------------------------------------------------------
# Logged in
# -------------------------------------------------------------------------------------------------
else:
    print(type(cookies['user_info']))
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
        auth_functions.sign_out(cookies)
        pg = st.navigation(
            [st.Page("./pages/demo.py", title="Video Demo")], position="hidden"
        )
        pg.run()
        st.rerun()
        
    def dashboard():
        from pages.dashboard import main
        main(cookies=cookies)
    def chat():
        from pages.chat import main
        main(cookies=cookies, root=root, session=session)
    def add_talent():
        from pages.add_talent import main
        main(cookies=cookies)
    def settings():
        from pages.settings import main
        main(cookies=cookies)
        
    dashboard_page = st.Page(dashboard, title="Dashboard", icon=":material/dashboard:")
    chat_page = st.Page(chat, title="PM Assistant", icon=":material/chat:")
    add_talent_page = st.Page(add_talent, title="Add IT Talent", icon=":material/person_add:"
    )
    settings_page = st.Page(settings, title="Settings", icon=":material/settings:"
    )
    logout = st.Page(logout, title="Log out", icon=":material/logout:")
    pg = st.navigation(
        [dashboard_page, chat_page, add_talent_page, settings_page, logout],
        position="sidebar",
        expanded=True,
    )
    
    pg.run()
