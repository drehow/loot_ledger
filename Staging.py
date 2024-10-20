page_name = 'Staging'

import streamlit as st
from streamlit import session_state as ss

import utils.appearance as a
import backend.serv_staging as serv
import frontend.ui_staging as ui
import utils.init as i
import callbacks.cb_staging as cb
import utils.preview as p

a.page_config(page_name)
a.css()
i.init(page_name)

c1_staging, c2_staging = st.columns(2)
with c1_staging:
    st.selectbox('Account', ss.ranked_accounts, ss.selected_account_index, on_change=cb.chg_selected_account, key='account_select_home') 
with c2_staging: 
    st.selectbox('Month', ss.months_list, ss.init_month_select_home, key='month_select_home', on_change=cb.staging_month_select)

t1, t2, t3, t4, t5 = st.tabs(['Single transaction',
                            'Multiple transactions', 
                            'Add an account balance',
                            'Edit saved transactions',
                            'Edit a saved account balance'])

with t1:
    st.markdown('**Enter a single transaction**')
    ui.single_trans_inputs()
    ui.display_errors('single_trans_inputs')
    st.markdown('---')
    ui.buttons('single_trans_inputs')
    st.markdown('---')
    p.preview_account_activity()

with t2:
    st.markdown('**Enter multiple transactions**')
    ui.multi_trans_input()
    ui.display_errors('multi_trans_input')
    st.markdown('---')
    ui.buttons('multi_trans_input')
    st.markdown('---')
    p.preview_account_activity()

with t3:
    st.markdown('**Add an account balance**')
    ui.account_balance_input()
    ui.display_errors('account_balance_input')
    st.markdown('---')
    ui.buttons('account_balance_input')
    st.markdown('---')
    p.preview_account_activity()

serv.reset_ss_vars()

