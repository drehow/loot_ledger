import streamlit as st
from streamlit import session_state as ss
import pandas as pd


import utils.appearance as a
page_name = 'Home'
a.page_config(page_name)

import utils.init as i
i.init(page_name)

st.subheader(page_name)
st.markdown('---')


def chg_selected_account():
    ss.selected_account_index = int(ss.ranked_accounts[ss.ranked_accounts == ss.account_select_home].index[0])
st.selectbox('Account', ss.ranked_accounts, ss.selected_account_index, on_change=chg_selected_account, key='account_select_home')

t1, t2, t3 = st.tabs(['Single transaction', 'Input a table', 'to-do'])

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
    
    c1, c2 = st.columns(2)
    with c1:
        st.text_input('Description', key='description_input_home')
        st.number_input('Amount', key='amount_input_home')
    with c2:
        st.selectbox('Category', ss.categories['NAME'], key='category_select_home')
        st.date_input('Date', key='date_input_home')
        
    if ss.category_select_home == 'Transfer':
        c3, c4 = st.columns(2)
        with c3:
            st.selectbox('Account to/from:', ranked_accounts, key='transfer_account_name_home')

    st.button('Add transaction', key='add_transaction_button_home')

    st.table(ss.transactions_month.head())

    st.button('Push transactions to db', key='commit_transaction_button_home')
            


# Initialize connection.
# conn = st.connection("snowflake")

# Perform query.
# df = conn.query("SELECT * from fin.category;", ttl=600)


# Print results.
# for row in df.itertuples():
#     st.write(f"{row.NAME} has a {row.ID}")


# st.subheader('holy shit we are connected to a cloud snowflake database that is awesome')