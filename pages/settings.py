import streamlit as st
import functions.auth_functions as auth_functions

st.markdown("<div><h2 style='padding:10px 0'>Settings</h2></div><br/>", unsafe_allow_html=True)

def destroy():
  print('Destroy all data')

st.markdown("<b>Delete All Data IT Talent</b>", unsafe_allow_html=True)
st.button(label='Delete All Data IT Talent', on_click=destroy, type='primary')

st.markdown("<br/>", unsafe_allow_html=True)


st.markdown("<b>Request To Delete Account</b>", unsafe_allow_html=True)
password = st.text_input(label='Confirm your password', type='password')
st.button(label='Delete Account', on_click=auth_functions.delete_account, args=[password], type='primary')


