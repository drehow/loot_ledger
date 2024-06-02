page_name = 'Staging'

import streamlit as st
from streamlit import session_state as ss
import pandas as pd
from datetime import datetime, timedelta

import utils.appearance as a
import utils.transaction_mgmt_server as serv
import utils.transaction_mgmt_ui as ui
import utils.querying as q
import utils.init as i
import utils.misc as m

a.page_config(page_name)
a.css()
i.init(page_name)
cb = serv.staging_callbacks()
c1_staging, c2_staging = st.columns(2)
with c1_staging:
    st.selectbox('Account', ss.ranked_accounts, ss.selected_account_index, on_change=cb['chg_selected_account'], key='account_select_home') 

with c2_staging: 
    # st.date_input('Date', value=ss.init_date_input_home, format="MM/DD/YYYY", on_change=cb['chg_single_trans_inputs'], key='date_input_home')
    def staging_month_select():
        ss.init_month_select_home = ss.months_list.index(ss.month_select_home)
        ss.date_input_home = m.eom(datetime.strptime(ss.month_select_home, '%b, %Y').date())
    st.selectbox('Month', ss.months_list, ss.init_month_select_home, key='month_select_home', on_change=staging_month_select)

t1, t2, t4 = st.tabs(['Single transaction', 'Input a table', 'Delete a transaction'])

with t1:
    ui.single_trans_input()
    serv.preview()
with t2:
    ui.multi_trans_input()
    serv.preview()

serv.reset_ss_vars()