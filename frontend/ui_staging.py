import streamlit as st
from streamlit import session_state as ss
import pandas as pd

import backend.serv_staging as serv
import callbacks.cb_staging as cb
import utils.misc as m
import utils.appearance as a
import utils.preview as p


####################################### SINGLE TRANSACTION INPUT #######################################
def single_trans_inputs():

    c1, c2 = st.columns(2)
    with c1:
        st.text_input('Description', value=ss.init_description, on_change=cb.chg_single_trans_inputs, 
                      key='description_input_home')
        st.number_input('Amount', value = ss.init_amount_input_home, on_change=cb.chg_single_trans_inputs, 
                        key='amount_input_home')
    with c2:
        st.selectbox('Category', ss.categories['NAME'], ss.init_category_select_home, on_change=cb.chg_single_trans_inputs, key='category_select_home')
        st.date_input('Transaction Date', ss.init_single_trans_date_input, format='MM/DD/YYYY', 
                       key = 'single_trans_date_input', on_change=cb.chg_single_trans_inputs)
    
    if ss.transfer_transaction_single:
        c1_single_inputs, c2_single_inputs = st.columns(2)
        with c1_single_inputs:
            st.selectbox('Account to/from:', ss.ranked_accounts, None, on_change=cb.chg_single_trans_transfer, key='transfer_account_name_home')
        



def buttons(section):


    if section == 'single_trans_inputs':
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.button('Add draft transaction', 
                    key='add_transaction_button_home_single', 
                    use_container_width=True,
                    on_click=cb.add_temp_transaction_single)
        with c2:
            st.button('Clear top draft transaction', 
                    on_click=cb.clear_top_draft_trans, 
                    key='clear1_transaction_button_home_single', 
                    use_container_width=True)
        with c3:
            st.button('Clear draft transactions', 
                        on_click=cb.clear_draft_trans, 
                        key='clearAll_transaction_button_home_single', 
                        use_container_width=True)
        with c4:
            st.button('Save draft transactions', 
                    key='commit_transaction_button_home_single', 
                    use_container_width=True)
            

    if section == 'multi_trans_input':
        c1, c2, c3 = st.columns(3)
        with c1:
            st.button('Add draft transactions', 
                    key='add_transactions_button_home_multi', 
                    use_container_width=True,
                    on_click=cb.add_temp_transaction_multi
                    )
        with c2:
            st.button('Clear added transactions', 
                        on_click=cb.clear_draft_trans, 
                        key='clearAll_transaction_button_home_multi', 
                        use_container_width=True)
        with c3:
            st.button('Save draft transactions', 
                    key='commit_transaction_button_home_multi', 
                    use_container_width=True)
            
    if section == 'account_balance_input':

        c1_ab, c2_ab, c3_ab = st.columns(3)
        with c1_ab:
            st.button('Add account balance', 
                    key='add_account_balance_button_home', 
                    use_container_width=True,
                    on_click=cb.add_temp_account_balance
                    )
        with c2_ab:
            st.button('Clear account balance', 
                    #   on_click=cb.clear_draft
                        key='clear_account_balance_button_home',
                        use_container_width=True)
                        
        with c3_ab:
            st.button('Save account balance', 
                    key='commit_account_balance_button_home', 
                    use_container_width=True)

        
    # p.preview_transactions(account = ss.chosen_account, 
    #                        date = ss.date_input_home, 
    #                        draft_trans = ss.draft_trans, 
    #                        saved_trans = saved_trans)

####################################### MULTIPLE TRANSACTION INPUT #######################################
def multi_trans_input():
    
    
    if 'multi_trans_init' not in ss:
        ss.multi_trans_init = pd.DataFrame({
            'Date':[ss.date_input_home], 
            'Description':[None], 
            'Amount':[0], 
            'Category':['Unknown transactions'], 
            'Transfer Account':[None],
            })
        ss.multi_trans_init['Date'] = pd.to_datetime(ss.multi_trans_init['Date']).dt.date
    
    if 'multi_trans_input' not in ss:
        ss['multi_trans_input'] = ss.multi_trans_init

    st.data_editor(ss.multi_trans_init, 
            column_config={
                "Date": st.column_config.DateColumn("Date",format="MM/DD/YYYY",step=1,),
                "Amount": st.column_config.NumberColumn("Amount",step=0.01,format="%.2f"),
                "Category": st.column_config.SelectboxColumn("Category",options=ss.categories['NAME']),
                "Transfer Account": st.column_config.SelectboxColumn("Transfer Account",options=ss.ranked_accounts)
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            # on_change=cb.mult_trans_input_changes,
            key='multi_trans_input_edited'
        )


    # serv.check_for_errors_multi()

    

    
    # p.preview_transactions(account = ss.chosen_account, 
    #                        date = ss.date_input_home, 
    #                        draft_trans = ss.draft_trans, 
    #                        saved_trans = ss.saved_trans)

####################################### ADD ACCOUNT BALANCE #######################################
def account_balance_input():
    
    c1, c2 = st.columns(2)
    with c1:
        st.date_input('Date', ss.date_input_home, format='MM/DD/YYYY', 
                      key='date_input_accountBalance', 
                      on_change=cb.chg_account_balance_inputs
                      )
    with c2:
        st.number_input('Amount', value = ss.account_balance_input, 
                        on_change=cb.chg_account_balance_inputs, 
                        key='amount_input_accountBalance')
        
    # serv.check_for_errors_accountBalance()
    
    # st.markdown('---')

    
    # st.markdown('---')

    # p.preview_transactions(account = ss.chosen_account, 
    #                        date = ss.date_input_home, 
    #                        draft_trans = ss.draft_trans, 
    #                        saved_trans = ss.saved_trans)


def display_errors(section):
    message = ''
    if section == 'single_trans_inputs':
        if ss.zero_amount_error:
            message = message + '* Amount cannot be zero. \n'
        if ss.blank_description_error:
            message = message + '* Descriptions cannot be blank.\n'
        if ss.date_error:
            message = message + '* Dates must be within the selected month.\n'
        if ss.empty_transfer_account:
            message = message + '* To submit a Transfer, select an account to transfer to/from.\n'
        if ss.same_accounts_error:
            message = message + '* Cannot transfer to the same account.'
    if section == 'multi_trans_input':
        if ss.zero_amount_error_multi:
            message = message + '* Amounts cannot be zero.\n'
        if ss.blank_description_error_multi:
            message = message + '* Descriptions cannot be blank.\n'
        if ss.date_error_multi:
            message = message + '* Dates must be within the selected month.\n'
        if ss.empty_transfer_account_multi:
            message = message + '* To submit a Transfer, select an account to transfer to/from.\n'
        if ss.same_accounts_error_multi:
            message = message + '* Cannot transfer to the same account.\n'
        if ss.blank_category_error_multi:
            message = message + '* Categories cannot be blank.'
    
    if section == 'account_balance_input':
        if ss.empty_balance_account:
            message = message + '* Balance is empty.\n'
        if ss.date_future_error_account:
            message = message + '* Date cannot be in the future.\n'
        if ss.date_error_account:
            message = message + '* Date must be within the selected month.'
    if message != '':
        st.error('Errors in inputs: \n'+ message)

    