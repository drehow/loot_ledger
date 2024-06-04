import streamlit as st
from streamlit import session_state as ss
import pandas as pd

import utils.transaction_mgmt_server as serv

cb = serv.staging_callbacks()

def single_trans_input():

    st.markdown('**Enter a single transaction**')
    
    c1, c2 = st.columns(2)
    with c1:
        st.text_input('Description', value=ss.init_description, on_change=cb['chg_single_trans_inputs'], 
                      key='description_input_home')
        if ss.blank_description_error:
            st.error('Description cannot be blank.')
        st.number_input('Amount', value = ss.init_amount_input_home, on_change=cb['chg_single_trans_inputs'], 
                        key='amount_input_home')
    with c2:
        st.selectbox('Category', ss.categories['NAME'], ss.init_category_select_home, on_change=cb['chg_single_trans_inputs'], key='category_select_home')
        st.date_input('Transaction Date', ss.init_single_trans_date_input, format='MM/DD/YYYY', 
                       key = 'single_trans_date_input', on_change=cb['chg_single_trans_inputs'])
        
    # if ss.category_select_home == 'Transfer':
    #     ss.transfer_transaction = True
    #     c1_single_inputs, c2_single_inputs = st.columns(2)
    #     with c1_single_inputs:
    #         st.selectbox('Account to/from:', ss.ranked_accounts, None, on_change=cb['chg_single_trans_transfer'], key='transfer_account_name_home')
    #         if ss.empty_transfer_account:
    #             st.error('To submit a Transfer, select an account to transfer to/from.')
    #         if ss.same_accounts_error:
    #             st.error('Cannot transfer to the same account.')

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
    st.markdown('---')

def multi_trans_input():
    df = pd.DataFrame(index=range(1), columns=['Date', 'Description', 'Amount', 'Category', 'Transfer Account'])
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    
    if 'multi_trans_input' not in ss:
        ss['multi_trans_input'] = df

    def apply_changes_data_editor(df, changes):
        # st.write(changes)
        if "edited_rows" in changes:
            for row_index, row_changes in changes["edited_rows"].items():
                for column, new_value in row_changes.items():
                    df.at[int(row_index), column] = new_value
        
        if "added_rows" in changes:
            added_rows = changes["added_rows"]
            new_rows = [row_values for row_values in added_rows]
            new_rows = pd.DataFrame(new_rows)
            df = pd.concat([df, new_rows]).reset_index(drop=True)
        
        return df

    def mult_trans_input_changes():
        ss.multi_trans_input = apply_changes_data_editor(df, ss.multi_trans_input_edited)
        ss.input_table_changed = True

    st.data_editor(df, 
                   column_config={
                        "Date": st.column_config.DateColumn(
                            "Date",
                            format="MM/DD/YYYY",
                            step=1,
                        ),
                        "Amount": st.column_config.NumberColumn(
                            "Amount",
                            step=0.01,
                            format="%.2f"
                        ),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=ss.categories['NAME']
                        ),
                        "Transfer Account": st.column_config.SelectboxColumn(
                            "Transfer Account",
                            options=ss.ranked_accounts
                        )
                    },
                    hide_index=False,
                    use_container_width=True,
                    num_rows="dynamic",
                    on_change=mult_trans_input_changes,
                    key='multi_trans_input_edited'
        )

    st.table(ss.multi_trans_input)

    st.markdown('---')

