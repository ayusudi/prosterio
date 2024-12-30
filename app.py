import streamlit as st

if "page" not in st.session_state:
    st.session_state.page = ""

PAGE = [None, "Dashboard", "PM Assistant", "Add IT Talent", ]

def login():
    st.header("Log in")
    if st.button("Log in"):
        st.session_state.page = "Dashboard"
        print(st.session_state.page)
        st.rerun()

def logout():
    st.session_state.page = None
    st.rerun()

page = st.session_state.page
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
dashboard_page = st.Page("dashboard.py", title="Dashboard", icon=":material/dashboard:")
chat_page = st.Page("chat.py", title="PM Assistant", icon=":material/chat:")
add_talent_page = st.Page("add_talent.py", title="Add IT Talent", icon=":material/person_add:")


st.title("Prosterio")

# st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

page_dict = {}

if st.session_state.page == None or st.session_state.page == "":
  pg = st.navigation([st.Page(login, title="Login")])
else:
  pg = st.navigation([dashboard_page, chat_page, add_talent_page, logout_page])

pg.run()