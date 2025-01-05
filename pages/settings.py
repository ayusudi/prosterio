import streamlit as st
import functions.auth_functions as auth_functions
from functions.header import header

header("⚙️", "Settings")


def destroy():
    print("Destroy all data")


st.markdown("<b>Delete All Data IT Talent</b>", unsafe_allow_html=True)
st.button(label="Delete All Data IT Talent", on_click=destroy, type="primary")

st.markdown("<br/>", unsafe_allow_html=True)


st.markdown("<b>Request To Delete Account</b>", unsafe_allow_html=True)
password = st.text_input(label="Confirm your password", type="password")
st.button(
    label="Delete Account",
    on_click=auth_functions.delete_account,
    args=[password],
    type="primary",
)
