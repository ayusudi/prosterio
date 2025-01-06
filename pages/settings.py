import streamlit as st
import functions.auth_functions as auth_functions
from functions.header import header
from functions.connection import destroy

header("⚙️", "Settings")

st.markdown("<b>Delete All Data IT Talent</b>", unsafe_allow_html=True)
st.button(
    label="Delete All Data IT Talent",
    on_click=destroy,
    args=[st.session_state.user_info["email"]],
    type="primary",
)

st.markdown("<br/>", unsafe_allow_html=True)

st.markdown("<b>Request To Delete Account</b>", unsafe_allow_html=True)
password = st.text_input(label="Confirm your password", type="password")
st.button(
    label="Delete Account",
    on_click=auth_functions.delete_account,
    args=[password],
    type="primary",
)
