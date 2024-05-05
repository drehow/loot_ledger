import streamlit as st
from streamlit import session_state as ss

import utils.querying as q

def init(page):
    if 'accounts' not in ss:
        ss['accounts'] = q.query('get_accounts')