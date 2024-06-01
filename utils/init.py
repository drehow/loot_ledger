import streamlit as st
from streamlit import session_state as ss
import pandas as pd

import utils.querying as q



def init(page):

    if 'accounts' not in ss:
        ss['accounts'] = q.query('get_accounts')
        ss['accounts'].columns = ss['accounts'].columns.str.upper()
    if 'ranked_accounts' not in ss:
        ss['ranked_accounts'] = ss.accounts.sort_values(['AUTOMATED','RA_SCORE'], ascending=[True, False])['NAME'].reset_index(drop=True)
        # st.table(ss.ranked_accounts)

    if 'categories' not in ss:
        ss['categories'] = q.query('get_categories')
        ss['categories'].columns = ss['categories'].columns.str.upper()
    if 'account_balances' not in ss:
        ss['account_balances'] = q.query('get_account_balances')
        ss['account_balances'].columns = ss['account_balances'].columns.str.upper()

    if page == 'Staging':
        defaults = {
            'init_description': None,
            'write_description': None,
            'selected_account_index': 0,
            'init_category_select_home': ss.categories[ss.categories['NAME']=='Unknown transactions'].index[0].item(),
            'init_amount_input_home': 0,
            'init_date_input_home': pd.to_datetime('today').date(),
            'transfer_account_name_home': 0,
            'init_transfer_account_name_home': 0,
            'chosen_account': ss.ranked_accounts[0],
            'debit': ss.accounts['ASSET'][0].item() == 1,
            'new_selection': False,
            'draft_trans': pd.DataFrame(),
            'empty_transfer_account': False,
            'same_accounts_error': False,
            'blank_description_error': False,
            'transfer_transaction': False,
        }
    
    else:
        return
    
    for key, default_val in defaults.items():
        if key not in ss:
            ss[key] = default_val