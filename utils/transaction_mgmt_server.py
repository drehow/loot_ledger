import utils.querying as q
import utils.appearance as a
import utils.misc as m

import streamlit as st
from streamlit import session_state as ss

import pandas as pd

def get_mat_table(end_date, account):
    start_date = end_date.replace(day=1).strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    args = {
        0: start_date,
        1: end_date,
        2: account,
    }
    t1 = q.query('get_transactions_date_range', args)
    t1['FROM_DB'] = True
    return t1

def calc_month_stats(month_account_trans):
    if month_account_trans.empty:
        stats = {
            'inflow': 0,
            'outflow': 0,
            'correction': 0,
            'unknown': 0,
        }
    else:
        stats = {
        'inflow': month_account_trans[
            (month_account_trans['AMOUNT'] > 0) & 
            ~(month_account_trans['CATEGORY'].isin(['Unknown transactions', 'Correction for Balance']))
            ]['AMOUNT'].sum(),
        'outflow': month_account_trans[
            (month_account_trans['AMOUNT'] <= 0) & 
            ~(month_account_trans['CATEGORY'].isin(['Unknown transactions', 'Correction for Balance']))
            ]['AMOUNT'].sum(),
        'correction': month_account_trans[
            (month_account_trans['CATEGORY'] == 'Correction for Balance')
            ]['AMOUNT'].sum(),
        'unknown': month_account_trans[
            (month_account_trans['CATEGORY'] == 'Unknown transactions')
            ]['AMOUNT'].sum(),
        }
    return stats

# get the most recent account balance before the start_date
def mat_summary(chosen_account, date_input_home, mat_stats):
    prev_bal = ss.account_balances[
        (ss.account_balances['NAME'] == chosen_account) &
        (ss.account_balances['DATE'] < date_input_home.replace(day=1))
        ].sort_values('DATE', ascending=False).iloc[0]['BALANCE']
    prev_bal = float(prev_bal)
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
        st.metric('Starting balance', f"{round(prev_bal,0):,}")
    with c2:
        a.prettyMetric('Inflow', mat_stats['inflow'], '#1a7f19')
    with c3:
        a.prettyMetric('Outflow', mat_stats['outflow'], '#a61919')
    with c4:
        a.prettyMetric('Corrections', mat_stats['correction'], '#8f8550')
    with c5:
        a.prettyMetric('Unknown', mat_stats['unknown'], '#8f8550')
    with c6:
        st.metric('Calculated ending balance', f"{round(calc_end_bal,0):,}")

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
    st.markdown('---')
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
        ss.init_date_input_home = ss['date_input_home']

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
                'DATE': [ss.init_date_input_home],
                'CATEGORY': [ss.categories['NAME'][ss.init_category_select_home]],
                'FROM_DB': [False],
            })
            add_to_draft_trans()


    def clear_top_draft_trans():
        ss.draft_trans = ss.draft_trans.iloc[1:]
        ss.edited_mat = True
        ss.add = True
    
    return {
        'clear_draft_trans': clear_draft_trans,
        'chg_selected_account': chg_selected_account,
        'chg_single_trans_inputs': chg_single_trans_inputs,
        'chg_single_trans_transfer': chg_single_trans_transfer,
        'add_temp_transaction_single': add_temp_transaction_single,
        'clear_top_draft_trans': clear_top_draft_trans
    }

def reset_ss_vars():
    ss.new_selection = False 
    ss.empty_transfer_account = False
    ss.same_accounts_error = False
    ss.blank_description_error = False
