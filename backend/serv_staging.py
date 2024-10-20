import utils.querying as q
import utils.appearance as a
import utils.misc as m

import streamlit as st
from streamlit import session_state as ss

import pandas as pd
from datetime import datetime

def month_transactions(end_date, account):
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
    t1['ACCOUNT'] = account
    return t1

def calc_month_stats(month_account_trans, account):

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

    debit = ss.accounts['ASSET'][ss.accounts['NAME'] == account].item() == 1
    prev_bal = float(ss.account_balances[
        (ss.account_balances['NAME'] == account) &
        (ss.account_balances['DATE'] < ss.date_input_home.replace(day=1))
        ].sort_values('DATE', ascending=False).iloc[0]['BALANCE'])
    
    stats['prev_bal'] = prev_bal

    if (not ss.draft_balance.empty) & (account in ss.draft_balance['ACCOUNT'].values):
        if account in ss.draft_balance['ACCOUNT'].values:
            end_bal = ss.draft_balance['BALANCE'][(ss.draft_balance['ACCOUNT'] == account) & \
                                                  (ss.draft_balance['DATE'] == m.eom(ss.date_input_home))].values[0]
        stats['correction'] = (end_bal - prev_bal) - (stats['inflow'] + stats['outflow'] + stats['unknown'] + stats['correction'])
    else:
        calc_end_bal = prev_bal + (
            stats['inflow'] + 
            stats['outflow'] + 
            stats['correction'] + 
            stats['unknown'] 
        ) * (1 if debit else -1)
        end_bal = calc_end_bal
    
    stats['end_bal'] = end_bal

    return stats



def get_month_balances(account):
    # debit = ss.accounts['ASSET'][ss.accounts['NAME'] == account].item() == 1
    # prev_bal = float(ss.account_balances[
    #     (ss.account_balances['NAME'] == account) &
    #     (ss.account_balances['DATE'] < ss.date_input_home.replace(day=1))
    #     ].sort_values('DATE', ascending=False).iloc[0]['BALANCE'])
    # if not ss.draft_balance.empty:
    #     if account in ss.draft_balance['ACCOUNT'].values:
    #         end_bal = ss.draft_balance['BALANCE'][(ss.draft_balance['ACCOUNT'] == account) & \
    #                                               (ss.draft_balance['DATE'] == m.eom(ss.date_input_home))].item()
    # else:
    #     end_bal = None
        # calc_end_bal = prev_bal + (
        #     activity_stats['inflow'] + 
        #     activity_stats['outflow'] + 
        #     activity_stats['correction'] + 
        #     activity_stats['unknown'] 
        # ) * (1 if debit else -1)
        # end_bal = calc_end_bal

    balances = {
        'prev_bal': prev_bal,
        'end_bal': end_bal,
    }
    return balances

def add_to_draft_trans(draft_trans_to_add):
    ss.draft_trans = pd.concat([
        draft_trans_to_add,
        ss.draft_trans
    ]).reset_index(drop=True)


def check_draft_trans_integrity_single(description):
    checks_out = True
    if (description is None) or (description == ''):
        ss.blank_description_error = True
        checks_out = False
    if ss.amount_input_home == 0:
        ss.zero_amount_error = True
        checks_out = False
    if (ss.single_trans_date_input < m.fom(ss.date_input_home)) or \
        (ss.single_trans_date_input > m.eom(ss.date_input_home)):
        ss.date_error = True
        checks_out = False
    if ss.transfer_transaction_single:
        if ss.transfer_account_name_home is None:
            ss.empty_transfer_account = True
            checks_out = False
        elif ss.transfer_account_name_home == ss.chosen_account:
            ss.same_accounts_error = True
            checks_out = False
    return checks_out

def check_draft_trans_integrity_multi():
    checks_out = True
    if any(ss.write_descriptions.isnull()):
        ss.blank_description_error_multi = True
        checks_out = False
    if any(ss.write_descriptions == ''):
        ss.blank_description_error_multi = True
        checks_out = False
    if any(ss.multi_trans_input['Category'].isnull()):
        ss.blank_category_error_multi = True
        checks_out = False
    if any(ss.multi_trans_input['Amount'] == 0) or \
        any(ss.multi_trans_input['Amount'].isnull()) or \
        any(ss.multi_trans_input['Amount'] == ''):
            ss.zero_amount_error_multi = True
            checks_out = False
    if any(ss.multi_trans_input['Date'].isnull()):
        ss.date_error_multi = True
        checks_out = False
    if any(ss.multi_trans_input['Date'] < m.fom(ss.date_input_home)) or any(ss.multi_trans_input['Date'] > m.eom(ss.date_input_home)):
        ss.date_error_multi = True
        checks_out = False
    if len(ss.transfer_transaction_multi) > 0:
        temp = ss.multi_trans_input[ss.multi_trans_input['Category'] == 'Transfer']
        if any(temp['Transfer Account'].isnull()):
            ss.empty_transfer_account_multi = True
            checks_out = False
        if any(temp['Transfer Account'] == ss.chosen_account):
            ss.same_accounts_error_multi = True
            checks_out = False
        temp = ss.multi_trans_input[ss.multi_trans_input['Category'] != 'Transfer']
        if not temp.empty:
            if any(temp['Transfer Account'].notnull()):
                ss.transfer_account_error = True
                checks_out = False
    return checks_out

def check_draft_balance_integrity():
    checks_out = True
    if ss.add_account_balance_button_home is None:
        ss.empty_balance_account = True
        checks_out = False
    if ss.date_input_home > datetime.today().date():
        ss.date_future_error_account = True
        checks_out = False
    if (ss.date_input_home < m.fom(ss.date_input_home)) or (ss.date_input_home > m.eom(ss.date_input_home)):
        ss.date_error_account = True
        checks_out = False
    return checks_out



# def check_for_errors_multi():
    

# def check_for_errors_accountBalance():  

    

def reset_ss_vars():
    ss.empty_transfer_account = False
    ss.empty_transfer_account_multi = False
    ss.blank_category_error_multi = False
    ss.same_accounts_error = False
    ss.same_accounts_error_multi = False
    ss.blank_description_error = False
    ss.blank_description_error_multi = False
    ss.zero_amount_error = False
    ss.zero_amount_error_multi = False
    ss.date_error = False
    ss.date_error_multi = False
    ss.transfer_account_error = False
    ss.date_future_error_account = False
    ss.date_error_account = False
    # ss.transfer_transaction_single = False
    # ss.refresh_saved_transactions = False
    


