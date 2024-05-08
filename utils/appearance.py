import streamlit as st
from streamlit import session_state as ss



def page_config(title):
    st.set_page_config(
        layout = "wide",
        page_title = title,
        page_icon = ":spy:",
        initial_sidebar_state= 'collapsed',
    )

if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'
