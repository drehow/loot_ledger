import utils.querying as q
import utils.appearance as a
import utils.misc as m

import streamlit as st
from streamlit import session_state as ss

import pandas as pd
from datetime import datetime

def get_mat_table(end_date, account):
    start_date = end_date.replace(day=1).strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    # st.subheader(f"start_date: {start_date}, end_date: {end_date}, account: {account}")
    args = {
        0: start_date,
        1: end_date,
        2: account,
    }
    t1 = q.query('get_transactions_date_range', args)
    t1['FROM_DB'] = True
    return t1

def calc_month_stats(month_account_trans):
    # st.subheader('here')
    if month_account_trans.empty:
        stats = {
            'inflow': 0.0,
            'outflow': 0.0,
            'correction': 0.0,
            'unknown': 0.0,
        }

    else:
        stats = {
        'inflow': float(month_account_trans[
            (month_account_trans['AMOUNT'] > 0) & 
            ~(month_account_trans['CATEGORY'].isin(['Unknown transactions', 'Correction for Balance']))
            ]['AMOUNT'].sum()),
        'outflow': float(month_account_trans[
            (month_account_trans['AMOUNT'] <= 0) & 
            ~(month_account_trans['CATEGORY'].isin(['Unknown transactions', 'Correction for Balance']))
            ]['AMOUNT'].sum()),
        'correction': float(month_account_trans[
            (month_account_trans['CATEGORY'] == 'Correction for Balance')
            ]['AMOUNT'].sum()),
        'unknown': float(month_account_trans[
            (month_account_trans['CATEGORY'] == 'Unknown transactions')
            ]['AMOUNT'].sum()),
        }
    return stats

# get the most recent account balance before the start_date
def mat_summary(chosen_account, date_input_home, mat_stats):
    prev_bal = float(ss.account_balances[
        (ss.account_balances['NAME'] == chosen_account) &
        (ss.account_balances['DATE'] < date_input_home.replace(day=1))
        ].sort_values('DATE', ascending=False).iloc[0]['BALANCE'])
    calc_end_bal = prev_bal + (
        mat_stats['inflow'] + 
        mat_stats['outflow'] + 
        mat_stats['correction'] + 
        mat_stats['unknown'] 
    ) * (1 if ss.debit else -1)

    # summary_table = pd.DataFrame({
    #     '_': ['Starting balance', 'Inflow', 'Outflow', 'Corrections', 'Unknown', 'Calculated ending balance'],
    #     'Amount': [prev_bal['BALANCE'], mat_stats['inflow'], mat_stats['outflow'], mat_stats['correction'], mat_stats['unknown'], calc_end_bal]
    # })
    # return st.table(summary_table)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1:
        st.metric('Starting balance', f"{prev_bal:,.0f}")
    with c2:
        st.metric('Inflow', f'{mat_stats["inflow"]:,.0f}')
    with c3:
        st.metric('Outflow', f'{mat_stats["outflow"]:,.0f}')
    with c4:
        st.metric('Corrections', f'{mat_stats["correction"]:,.0f}')
    with c5:
        st.metric('Unknown', f'{mat_stats["unknown"]:,.0f}')
    with c6:
        st.metric('Calculated ending balance', f'{calc_end_bal:,.0f}')

def preview():

    if ('edited_mat' not in ss) or (ss.new_selection):
        ss.edited_mat = False

    if not ss.edited_mat:
        ss['saved_trans'] = get_mat_table(m.eom(ss.date_input_home), ss.chosen_account)
        ss['preview_trans'] = ss['saved_trans']
    elif ss.add:
        ss['preview_trans']  = pd.concat([ss.draft_trans, ss.saved_trans]).reset_index(drop=True)
        ss.add = False

    mat_stats = calc_month_stats(ss.preview_trans)
    
    mat_summary(ss.chosen_account, ss.date_input_home, mat_stats)
    # st.markdown('---')
    if not ss.preview_trans.empty:
        a.style_mat_table(ss.preview_trans)
    else:
        st.warning(f'No transactions found for **{ss.chosen_account}** in **{ss.date_input_home.strftime("%B %Y")}**')

def add_to_draft_trans():
    ss.draft_trans = pd.concat([
        ss.add_trans,
        ss.draft_trans
    ]).reset_index(drop=True)
    # st.table(ss.draft_trans)
    ss.edited_mat = True
    ss.add = True

def check_draft_trans_integrity():
    if (ss.write_description is None) or (ss.write_description == ''):
        ss.blank_description_error = True
        return False
    if ss.transfer_transaction:
        if ss.transfer_account_name_home is None:
            ss.empty_transfer_account = True
            return False
        elif ss.transfer_account_name_home == ss.chosen_account:
            ss.same_accounts_error = True
            return
    return True
        


def staging_callbacks():
    def clear_draft_trans():
        ss.draft_trans = pd.DataFrame()
        ss.edited_mat = True
        ss.add = True

    def staging_month_select():
        ss.init_month_select_home = ss.months_list.index(ss.month_select_home)
        ss.date_input_home = m.eom(datetime.strptime(ss.month_select_home, '%b, %Y').date())
        ss.init_single_trans_date_input = ss.date_input_home
        clear_draft_trans()
        ss.new_selection = True

    def chg_selected_account():
        ss.selected_account_index = int(ss.ranked_accounts[ss.ranked_accounts == ss.account_select_home].index[0])
        ss.chosen_account = ss.ranked_accounts[ss.selected_account_index]
        ss.debit = ss.accounts['ASSET'][ss.accounts['NAME']==ss.chosen_account].item() == 1
        clear_draft_trans()
        ss.new_selection = True

    def chg_single_trans_inputs():
        ss.init_description = ss['description_input_home']
        ss.init_amount_input_home = ss['amount_input_home']
        ss.init_category_select_home = int(ss.categories[ss.categories['NAME']==ss['category_select_home']].index[0])
        ss.init_single_trans_date_input = ss['single_trans_date_input']

    def chg_single_trans_transfer():
        if not ss.transfer_account_name_home is None:
            ss.init_transfer_account_name_home = int(ss.ranked_accounts[ss.ranked_accounts == ss.transfer_account_name_home].index[0])

    def add_temp_transaction_single():
        ss.write_description = ss.init_description
        good_draft = check_draft_trans_integrity()
        if good_draft:
            if ss.transfer_transaction:
                if ss.init_amount_input_home < 0:
                    ss.write_description = f"{ss.write_description} (transfer to {ss.ranked_accounts[ss.init_transfer_account_name_home]})"
                else:
                    ss.write_description = f"{ss.write_description} (transfer from {ss.ranked_accounts[ss.init_transfer_account_name_home]})"
                ss.transfer_transaction = False
            ss.add_trans = pd.DataFrame({
                'DESCRIPTION': [ss.write_description],
                'AMOUNT': [ss.init_amount_input_home],
                'DATE': [ss.single_trans_date_input],
                'CATEGORY': [ss.categories['NAME'][ss.init_category_select_home]],
                'FROM_DB': [False],
            })
            add_to_draft_trans()


    def clear_top_draft_trans():
        ss.draft_trans = ss.draft_trans.iloc[1:]
        ss.edited_mat = True
        ss.add = True

    # def multi_trans_input_callback():
        
    
    return {
        'clear_draft_trans': clear_draft_trans,
        'chg_selected_account': chg_selected_account,
        'chg_single_trans_inputs': chg_single_trans_inputs,
        'chg_single_trans_transfer': chg_single_trans_transfer,
        'add_temp_transaction_single': add_temp_transaction_single,
        'clear_top_draft_trans': clear_top_draft_trans,
        'staging_month_select': staging_month_select,
        # 'multi_trans_input_callback': multi_trans_input_callback,
    }

def reset_ss_vars():
    ss.new_selection = False 
    ss.empty_transfer_account = False
    ss.same_accounts_error = False
    ss.blank_description_error = False


