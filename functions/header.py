import streamlit as st

def header(emoji: str, title: str = ""):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 36px; line-height: 1; border-bottom: 2px solid CornflowerBlue; display:flex; padding-bottom:12px; gap:10px; font-weight:700">{emoji} <span style="font-size: 32px;">{title}</span></span>',
        unsafe_allow_html=True,
    )