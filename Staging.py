page_name = 'Staging'

import streamlit as st
from streamlit import session_state as ss
import pandas as pd

import utils.appearance as a
import utils.transaction_mgmt_server as serv
import utils.transaction_mgmt_ui as ui
import utils.querying as q
import utils.init as i

a.page_config(page_name)
a.css()
i.init(page_name)
cb = serv.staging_callbacks()

st.selectbox('Account', ss.ranked_accounts, ss.selected_account_index, on_change=cb['chg_selected_account'], key='account_select_home') 

t1, t2, t4 = st.tabs(['Single transaction', 'Input a table', 'Delete a transaction'])

with t1:
    ui.single_trans_inputs()
    serv.preview()

serv.reset_ss_vars()