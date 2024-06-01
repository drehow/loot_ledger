import streamlit as st
from streamlit import session_state as ss
import pandas as pd

import utils.transaction_mgmt_server as serv

cb = serv.staging_callbacks()

def single_trans_input():

    st.markdown('**Enter a single transaction**')
    
    c1, c2 = st.columns(2)
    with c1:
        st.text_input('Description', value=ss.init_description, on_change=cb['chg_single_trans_inputs'], key='description_input_home')
        if ss.blank_description_error:
            st.error('Description cannot be blank.')
        st.number_input('Amount', value = ss.init_amount_input_home, on_change=cb['chg_single_trans_inputs'], key='amount_input_home')
    with c2:
        st.selectbox('Category', ss.categories['NAME'], ss.init_category_select_home, on_change=cb['chg_single_trans_inputs'], key='category_select_home')
        st.date_input('Date', value=ss.init_date_input_home, format="MM/DD/YYYY", on_change=cb['chg_single_trans_inputs'], key='date_input_home')
        
    if ss.category_select_home == 'Transfer':
        ss.transfer_transaction = True
        c1_single_inputs, c2_single_inputs = st.columns(2)
        with c1_single_inputs:
            st.selectbox('Account to/from:', ss.ranked_accounts, None, on_change=cb['chg_single_trans_transfer'], key='transfer_account_name_home')
            if ss.empty_transfer_account:
                st.error('To submit a Transfer, select an account to transfer to/from.')
            if ss.same_accounts_error:
                st.error('Cannot transfer to the same account.')

    st.markdown('---')
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.button('Add temp transaction', 
                  key='add_transaction_button_home', 
                  use_container_width=True,
                  on_click=cb['add_temp_transaction_single'])
    with c2:
        st.button('Clear top added transaction', 
                  on_click=cb['clear_top_draft_trans'], 
                  key='clear1_transaction_button_home', 
                  use_container_width=True)
    with c3:
        st.button('Clear added transactions', 
                    on_click=cb['clear_draft_trans'], 
                    key='clearAll_transaction_button_home', 
                    use_container_width=True)
    with c4:
        st.button('Push added transactions to db', 
                  key='commit_transaction_button_home', 
                  use_container_width=True)

def multi_trans_input():
    df = pd.DataFrame(index=range(100), columns=['Date', 'Description', 'Amount', 'Category', 'Transfer Account'])
    st.data_editor(df, use_container_width=True)