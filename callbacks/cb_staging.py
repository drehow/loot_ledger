import pandas as pd
from datetime import datetime

import streamlit as st
from streamlit import session_state as ss

import utils.misc as m
import backend.serv_staging as serv


def clear_draft_trans():
    ss.draft_trans = pd.DataFrame()

def staging_month_select():
    ss.init_month_select_home = ss.months_list.index(ss.month_select_home)
    ss.date_input_home = m.eom(datetime.strptime(ss.month_select_home, '%b, %Y').date())
    ss.init_single_trans_date_input = ss.date_input_home
    clear_draft_trans()
    # ss.refresh_preview = True
    ss.refresh_saved_transactions = True

def chg_selected_account():
    ss.selected_account_index = int(ss.ranked_accounts[ss.ranked_accounts == ss.account_select_home].index[0])
    ss.chosen_account = ss.ranked_accounts[ss.selected_account_index]
    # ss.debit = ss.accounts['ASSET'][ss.accounts['NAME']==ss.chosen_account].item() == 1
    clear_draft_trans()
    # ss.refresh_preview = True
    ss.refresh_saved_transactions = True

def chg_single_trans_inputs():
    ss.init_description = ss['description_input_home']
    ss.init_amount_input_home = ss['amount_input_home']
    ss.init_category_select_home = int(ss.categories[ss.categories['NAME']==ss['category_select_home']].index[0])
    ss.transfer_transaction_single = (ss['category_select_home']=='Transfer')
    ss.init_single_trans_date_input = ss['single_trans_date_input']

def chg_single_trans_transfer():
    if not ss.transfer_account_name_home is None:
        ss.init_transfer_account_name_home = int(ss.ranked_accounts[ss.ranked_accounts == ss.transfer_account_name_home].index[0])

def add_temp_transaction_single():
    write_description = ss.init_description
    good_draft = serv.check_draft_trans_integrity_single(write_description)
    add_xfer = False
    if good_draft:
        if ss.transfer_transaction_single:
            xfer_account = ss.ranked_accounts[ss.init_transfer_account_name_home]
            wd_working = write_description
            if ss.init_amount_input_home < 0:
                write_description_main_acct = f"{wd_working} (transfer to {xfer_account})"
                write_description_xfer_acct = f"{wd_working} (transfer from {ss.chosen_account})"
            else:
                write_description_main_acct = f"{wd_working} (transfer from {xfer_account})"
                write_description_xfer_acct = f"{wd_working} (transfer to {ss.chosen_account})"
            
            draft_transfer = pd.DataFrame({
                'ACCOUNT': [xfer_account],
                'DESCRIPTION': [write_description_xfer_acct],
                'AMOUNT': [ - ss.init_amount_input_home],
                'DATE': [ss.single_trans_date_input],
                'CATEGORY': [ss.categories['NAME'][ss.init_category_select_home]],
                'FROM_DB': [False],
                'TRANSFER_ACCOUNT': [ss.chosen_account],
            })
        draft_trans_to_add = pd.DataFrame({
            'ACCOUNT': [ss.chosen_account],
            'DESCRIPTION': [write_description if not ss.transfer_transaction_single else write_description_main_acct],
            'AMOUNT': [ss.init_amount_input_home],
            'DATE': [ss.single_trans_date_input],
            'CATEGORY': [ss.categories['NAME'][ss.init_category_select_home]],
            'FROM_DB': [False],
            'TRANSFER_ACCOUNT': [xfer_account] if ss.transfer_transaction_single else [None],
        })
        if ss.transfer_transaction_single:
            draft_trans_to_add = pd.concat([draft_trans_to_add, draft_transfer])
        serv.add_to_draft_trans(draft_trans_to_add)
        # ss.transfer_transaction_single = False

def add_temp_transaction_multi():
    
    ss.multi_trans_input = m.apply_changes_data_editor(ss.multi_trans_init, ss.multi_trans_input_edited)
    ss.multi_trans_init = ss.multi_trans_input.copy()
    ss.multi_trans_init['Date'] = pd.to_datetime(ss.multi_trans_init['Date']).dt.date
    ss.multi_trans_input['Date'] = pd.to_datetime(ss.multi_trans_input['Date']).dt.date
    ss.multi_trans_input.dropna(how='all', inplace=True)
    if 'Transfer' in ss.multi_trans_input['Category'].values:
        ss.transfer_transaction_multi = ss.multi_trans_input[ss.multi_trans_input['Category'] == 'Transfer'].index.tolist()

    ss.write_descriptions = ss.multi_trans_input['Description']
    add_xfer = False
    good_draft = serv.check_draft_trans_integrity_multi()
    if good_draft:
        if len(ss.transfer_transaction_multi) > 0:
            write_descriptions_pres = ss.write_descriptions.copy()
            wd_xfer_accts = ss.write_descriptions.copy()
            xfer_trans_to_add = pd.DataFrame()
            add_xfer = True
            for i in ss.transfer_transaction_multi:
                
                if ss.multi_trans_input['Amount'][i] < 0:
                    ss.write_descriptions[i] = f"{write_descriptions_pres[i]} (transfer to {ss.multi_trans_input['Transfer Account'][i]})"
                    wd_xfer_accts[i] = f"{write_descriptions_pres[i]} (transfer from {ss.chosen_account})"
                else:
                    ss.write_descriptions[i] = f"{write_descriptions_pres[i]} (transfer from {ss.multi_trans_input['Transfer Account'][i]})"
                    wd_xfer_accts[i] = f"{write_descriptions_pres[i]} (transfer to {ss.chosen_account})"
                # st.write(ss.write_descriptions[i], wd_xfer_accts[i])
                xfer_trans_to_add_temp = pd.DataFrame({
                    'ACCOUNT': ss.multi_trans_input['Transfer Account'][i],
                    'DESCRIPTION': wd_xfer_accts[i],
                    'AMOUNT': - ss.multi_trans_input['Amount'][i],
                    'DATE': ss.multi_trans_input['Date'][i],
                    'CATEGORY': ss.multi_trans_input['Category'][i],
                    'FROM_DB': False,
                    'TRANSFER_ACCOUNT': ss.chosen_account,
                },index=[i])
                xfer_trans_to_add = pd.concat([xfer_trans_to_add, xfer_trans_to_add_temp])
                # st.table(xfer_trans_to_add)
            ss.transfer_transaction_multi = []
        draft_trans_to_add = pd.DataFrame({
            'ACCOUNT': [ss.chosen_account] * len(ss.write_descriptions),
            'DESCRIPTION': ss.write_descriptions,
            'AMOUNT': ss.multi_trans_input['Amount'],
            'DATE': ss.multi_trans_input['Date'],
            'CATEGORY': ss.multi_trans_input['Category'],
            'FROM_DB': [False] * len(ss.write_descriptions),
            'TRANSFER_ACCOUNT': ss.multi_trans_input['Transfer Account'],
        })
        # st.table(draft_trans_to_add)
        if add_xfer:
            # st.write('write here')
            draft_trans_to_add = pd.concat([
                draft_trans_to_add, xfer_trans_to_add
            ]).sort_index().reset_index(drop=True)
            add_xfer = False
        # st.table(draft_trans_to_add)
        serv.add_to_draft_trans(draft_trans_to_add)

def clear_top_draft_trans():
    if ss.draft_trans['CATEGORY'].iloc[0] == 'Transfer':
        ss.draft_trans = ss.draft_trans.iloc[2:]
    else:
        ss.draft_trans = ss.draft_trans.iloc[1:]

def mult_trans_input_changes():
    ss.multi_trans_input = m.apply_changes_data_editor(ss.multi_trans_init, ss.multi_trans_input_edited)
    # st.table(ss.multi_trans_init)
    ss.multi_trans_init['Date'] = pd.to_datetime(ss.multi_trans_init['Date']).dt.date
    ss.multi_trans_input['Date'] = pd.to_datetime(ss.multi_trans_input['Date']).dt.date
    ss.multi_trans_input.dropna(how='all', inplace=True)
    if 'Transfer' in ss.multi_trans_input['Category'].values:
        ss.transfer_transaction_multi = ss.multi_trans_input[ss.multi_trans_input['Category'] == 'Transfer'].index.tolist()

def chg_account_balance_inputs():
    ss.date_input_home = ss.date_input_accountBalance
    ss.account_balance_input = ss.amount_input_accountBalance


def add_to_draft_balance(draft_balance_to_add):
    ss.draft_balance = pd.concat([
        draft_balance_to_add,
        ss.draft_balance
    ]).reset_index(drop=True)

def add_temp_account_balance():
    st.write('here')
    good_draft = serv.check_draft_balance_integrity()
    if good_draft:
        st.write('good draft')
        ss.draft_balance = pd.DataFrame({
            'ACCOUNT': [ss.chosen_account],
            'BALANCE': [ss.account_balance_input],
            'DATE': [ss.date_input_home],
            'FROM_DB': [False],
            'MANUAL': [True],
        })
        add_to_draft_balance(ss.draft_balance)

