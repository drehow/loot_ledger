import streamlit as st
from streamlit import session_state as ss

import utils.querying as q



def init(page):


####################################
    ss['local_test'] = False
####################################


    if ss['local_test']:
        st.error('IN TESTING MODE')

    if 'accounts' not in ss:
        ss['accounts'] = q.query('get_accounts')
        ss['accounts'].columns = ss['accounts'].columns.str.upper()
    if 'ranked_accounts' not in ss:
        ss['ranked_accounts'] = ss.accounts.sort_values(['AUTOMATED','RA_SCORE'], ascending=[True, False])['NAME'].reset_index(drop=True)

    if 'categories' not in ss:
        ss['categories'] = q.query('get_categories')
        ss['categories'].columns = ss['categories'].columns.str.upper()
    if 'transactions_month' not in ss:
        ss['transactions_month'] = q.query('get_transactions_date_range')
        ss['transactions_month'].columns = ss['transactions_month'].columns.str.upper()

    if page == 'Home':
        if 'selected_account_index' not in ss:
            ss['selected_account_index'] = 0