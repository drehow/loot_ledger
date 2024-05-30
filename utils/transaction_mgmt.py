import utils.querying as q
import utils.appearance as a

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
        ].sort_values('DATE', ascending=False).iloc[0]
    if ss.debit:
        calc_end_bal = prev_bal['BALANCE'] + (
            mat_stats['inflow'] + 
            mat_stats['outflow'] + 
            mat_stats['correction'] + 
            mat_stats['unknown'] 
        )
    else:
        calc_end_bal = prev_bal['BALANCE'] - (
            mat_stats['inflow'] + 
            mat_stats['outflow'] + 
            mat_stats['correction'] + 
            mat_stats['unknown'] 
        )
    # summary_table = pd.DataFrame({
    #     '_': ['Starting balance', 'Inflow', 'Outflow', 'Corrections', 'Unknown', 'Calculated ending balance'],
    #     'Amount': [prev_bal['BALANCE'], mat_stats['inflow'], mat_stats['outflow'], mat_stats['correction'], mat_stats['unknown'], calc_end_bal]
    # })
    # return st.table(summary_table)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1:
        st.metric('Starting balance', f"{round(prev_bal['BALANCE'],0):,}")
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