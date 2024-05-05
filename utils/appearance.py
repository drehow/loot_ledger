import streamlit as st

def page_config(title):
    st.set_page_config(
        layout = "wide",
        page_title = title,
        page_icon = ":spy:",
    )