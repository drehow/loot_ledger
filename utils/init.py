import streamlit as st
from streamlit import session_state as ss

import utils.querying as q

def init(page):
    if 'accounts' not in ss:
        ss['accounts'] = q.query('get_accounts')
    if 'categories' not in ss:
        ss['categories'] = q.query('get_categories')
    if 'transactions_month' not in ss:
        ss['transactions_month'] = q.query('get_transactions_date_range')