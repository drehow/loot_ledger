import streamlit as st
from streamlit import session_state as ss
import pandas as pd

import utils.querying as q
import utils.misc as m

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

    if 'months_list' not in ss:
        ss.months_list = m.get_months_list()

    if page == 'Staging':
        if 'first_run_staging' not in ss:
            ss.first_run_staging = 0
            st.rerun()
            # workaround for a bug in Streamlit. If the first widget you edit is not on the first tab, it will jump back to first tab
            
        defaults = {
            'init_description': None,
            'write_description': None,
            'selected_account_index': 0,
            'init_month_select_home': 0,
            'init_category_select_home': ss.categories[ss.categories['NAME']=='Unknown transactions'].index[0].item(),
            'init_amount_input_home': 0.0,
            'init_single_trans_date_input': pd.to_datetime('today').date(),
            'date_input_home': pd.to_datetime('today').date(), # don't love the need for this one and the one above
            'transfer_account_name_home': 0,
            'init_transfer_account_name_home': 0,
            'chosen_account': ss.ranked_accounts[0],
            'debit': ss.accounts['ASSET'][0].item() == 1,
            'new_selection': False,
            'draft_trans': pd.DataFrame(),
            'empty_transfer_account': False,
            'empty_transfer_account_multi': False,
            'same_accounts_error': False,
            'same_accounts_error_multi': False,
            'blank_description_error': False,
            'blank_description_error_multi': False,
            'zero_amount_error': False,
            'zero_amount_error_multi': False,
            'transfer_transaction_single': False,
            'transfer_transaction_multi': [],
            'date_error': False,
            'date_error_multi': False,
        }
    
    else:
        return
    
    for key, default_val in defaults.items():
        if key not in ss:
            ss[key] = default_val