import utils.appearance as a

import streamlit as st
from streamlit import session_state as ss

page_name = 'Home'
a.page_config(page_name)
a.css()


import pandas as pd

import utils.misc as m
import utils.transaction_mgmt as tm
import utils.querying as q
import utils.init as i

####################

i.init(page_name)

st.subheader(page_name)
st.markdown('---')

if 'chosen_account' not in ss:
    ss.chosen_account = ss.ranked_accounts[ss.selected_account_index]
if 'debit' not in ss:
    ss.debit = ss.accounts['ASSET'][ss.accounts['NAME']==ss.chosen_account].item() == 1

def chg_selected_account():
    ss.selected_account_index = int(ss.ranked_accounts[ss.ranked_accounts == ss.account_select_home].index[0])
    ss.chosen_account = ss.ranked_accounts[ss.selected_account_index]
    ss.debit = ss.accounts['ASSET'][ss.accounts['NAME']==ss.chosen_account].item() == 1
    ss.new_selection = True

st.selectbox('Account', ss.ranked_accounts, ss.selected_account_index, on_change=chg_selected_account, key='account_select_home') 

t1, t2, t3, t4 = st.tabs(['Single transaction', 'Input a table', 'to-do', 'Delete a transaction'])

with t3:
    st.write('''trans table preview should show trans for that account/month, highlight any added, then not highlighted after push to db. Show headline stats in metrics below the table.
             \n Account dropdown needs to go above everything, and the update procedure will show
             \n drop to or from column and change other to "transfer account id"
             \n when adding transactions, need to have data checks for required fields. Namely, transfers need to have a transfer account. When a transfer is added to the preview, a second table will appear and show the other end of the transfer (if automated loan account, logic will apply and take out any unpaid interest for that month.
             \n table will be a data editor you can paste into, or you can click into the cells and edit. Still need to add a preview. Actually these could be on the same tab and just appear based on a toggle. I think you only want to be able to add bulk transactions for one account/month at a time. Date range will need to be a data check
             \n need a currency toggle
             \n put together a gitignored SQLite or Postgres db for developing without racking up snowflake costs
             \n cache aggressively, but set TTLs
             \n take a look at configs https://docs.streamlit.io/develop/api-reference/configuration/config.toml#client
             ''')


with t1:
    st.markdown('**Enter a single transaction**')
    
    def chg_single_trans_inputs():
        ss.init_description = ss['description_input_home']
        ss.init_amount_input_home = ss['amount_input_home']
        ss.init_category_select_home = int(ss.categories[ss.categories['NAME']==ss['category_select_home']].index[0])
        ss.init_date_input_home = ss['date_input_home']

    def chg_single_trans_transfer():
        ss.init_transfer_account_name_home = int(ss.ranked_accounts[ss.ranked_accounts == ss.transfer_account_name_home].index[0])

    c1, c2 = st.columns(2)
    with c1:
        st.text_input('Description', value=ss.init_description, on_change=chg_single_trans_inputs, key='description_input_home')
        st.number_input('Amount', value = ss.init_amount_input_home, on_change=chg_single_trans_inputs, key='amount_input_home')
    with c2:
        st.selectbox('Category', ss.categories['NAME'], ss.init_category_select_home, on_change=chg_single_trans_inputs, key='category_select_home')
        st.date_input('Date', value=ss.init_date_input_home, on_change=chg_single_trans_inputs, key='date_input_home')
        
    if ss.category_select_home == 'Transfer':
        c3, c4 = st.columns(2)
        with c3:
            st.selectbox('Account to/from:', ss.ranked_accounts, ss.init_transfer_account_name_home, on_change=chg_single_trans_transfer, key='transfer_account_name_home')


    def add_temp_transaction_single():
        ss.add_trans = pd.DataFrame({
            'DESCRIPTION': [ss.init_description],
            'AMOUNT': [ss.init_amount_input_home],
            'DATE': [ss.init_date_input_home],
            'CATEGORY': [ss.categories['NAME'][ss.init_category_select_home]],
            'FROM_DB': [False],
        })
        ss.edited_mat = True
        ss.add = True


    st.markdown('---')
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.button('Add temp transaction', 
                  key='add_transaction_button_home', 
                  use_container_width=True,
                  on_click=add_temp_transaction_single)
    with c2:
        st.button('Clear top added transaction', key='clear1_transaction_button_home', use_container_width=True)
    with c3:
        st.button('Clear added transactions', key='clearAll_transaction_button_home', use_container_width=True)
    with c4:
        st.button('Push added transactions to db', key='commit_transaction_button_home', use_container_width=True)


    # month accounts queried should exist separate. concat every time, if nothing added, concatting empty df will not change the table
    if ('edited_mat' not in ss) or (ss.new_selection):
        ss.edited_mat = False

    if not ss.edited_mat:
        ss['month_account_trans'] = tm.get_mat_table(m.eom(ss.date_input_home), ss.chosen_account)
    elif ss.add:
        ss['month_account_trans'] = pd.concat([ss.add_trans, ss['month_account_trans']]).reset_index(drop=True)
        ss.add = False

    # st.table(ss.accounts)

    
    mat_stats = tm.calc_month_stats(ss.month_account_trans)

    # get the most recent account balance before the start_date
    prev_bal = ss.account_balances[
        (ss.account_balances['NAME'] == ss.chosen_account) &
        (ss.account_balances['DATE'] < ss.date_input_home.replace(day=1))
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


    mat_styled = a.stlye_mat_table(ss.month_account_trans)
    st.markdown(mat_styled.hide(axis="index").to_html(), unsafe_allow_html=True)
   
            


# Initialize connection.
# conn = st.connection("snowflake")

# Perform query.
# df = conn.query("SELECT * from fin.category;", ttl=600)


# Print results.
# for row in df.itertuples():
#     st.write(f"{row.NAME} has a {row.ID}")


# st.subheader('holy shit we are connected to a cloud snowflake database that is awesome')