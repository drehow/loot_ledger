import streamlit as st
from streamlit import session_state as ss
import streamlit as st
import pandas as pd

import backend.serv_staging as serv
import utils.appearance as a
import utils.misc as m


def preview_summary_line(activity):
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1:
        st.metric('Starting balance', f"{activity['prev_bal']:,.0f}")
    with c2:
        st.metric('Inflow', f'{activity["inflow"]:,.0f}')
    with c3:
        st.metric('Outflow', f'{activity["outflow"]:,.0f}')
    with c4:
        st.metric('Corrections', f'{activity["correction"]:,.0f}')
    with c5:
        st.metric('Unknown', f'{activity["unknown"]:,.0f}')
    with c6:
        if activity['correction'] != 0:
            message = '**Manual Ending Balance**'
        else:
            message = 'Calculated Ending Balance'
        st.metric(message, f'{activity["end_bal"]:,.0f}')


def preview_account_activity():
    if ss.refresh_saved_transactions:
        ss.saved_trans = serv.month_transactions(m.eom(ss.date_input_home), ss.chosen_account)
        ss.preview_trans = ss.saved_trans  
        ss.refresh_saved_transactions = False 
    else:
        ss.preview_trans = pd.concat([ss.draft_trans, ss.saved_trans])
    if ss.preview_trans.empty:
        st.warning(f'No transactions found for **{ss.chosen_account}** in **{ss.date_input_home.strftime("%B %Y")}**')
        # st.stop()
    else:    
        
        accounts = ss.preview_trans['ACCOUNT'].unique()

        # reorder accounts so that chosen one shows up first
        account_headers = accounts.tolist() 
        account_headers.remove(ss.chosen_account)
        account_headers.insert(0, ss.chosen_account)
        account_headers = [f'{account} (transfers)' if account != ss.chosen_account else account for account in account_headers]

        tabs = st.tabs(account_headers)

        def add_correction(preview_trans_temp, activity, account):
            if activity['correction'] != 0:
                correction = pd.DataFrame({
                    'ACCOUNT': [account],
                    'DESCRIPTION': ['Correction for Balance'],
                    'CATEGORY': ['Correction for Balance'],
                    'AMOUNT': [activity['correction']],
                    'DATE': [m.eom(ss.date_input_home)],
                    'FROM_DB': [False],
                })
                ss.preview_trans = pd.concat([correction, ss.preview_trans]).reset_index(drop=True)
                # st.table(preview_trans_temp)
                preview_trans_temp = pd.concat([correction, preview_trans_temp]).reset_index(drop=True)
                # st.table(preview_trans_temp)
                ss.draft_trans = pd.concat([correction, ss.draft_trans]).reset_index(drop=True)
            # else:
            #     st.write('here')
                
            return preview_trans_temp

        for i, tab in enumerate(tabs):
            preview_trans_temp = ss.preview_trans[ss.preview_trans['ACCOUNT'] == accounts[i]]
            if i>0:
                saved_trans = serv.month_transactions(m.eom(ss.date_input_home), accounts[i])
                # st.write(not saved_trans.empty)
                if not saved_trans.empty:
                    preview_trans_temp = pd.concat([preview_trans_temp, saved_trans]).reset_index(drop=True)
            
            # st.write(preview_trans_temp)
            preview_trans_temp = preview_trans_temp[preview_trans_temp['ACCOUNT'] == accounts[i]].reset_index(drop=True)
            preview_trans_temp['AMOUNT'] = preview_trans_temp['AMOUNT'].astype(float)
            # balances = serv.get_month_balances(accounts[i])
            activity = serv.calc_month_stats(preview_trans_temp, accounts[i])
            preview_trans_temp = add_correction(preview_trans_temp, activity, accounts[i])
            
            with tab:
                preview_summary_line(activity)
                a.style_mat_table(preview_trans_temp)
