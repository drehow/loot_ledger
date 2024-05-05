import streamlit as st
from streamlit import session_state as ss
import pandas as pd

import utils.init as i
import utils.appearance as a

page_name = 'Home'
a.page_config(page_name)
i.init(page_name)
st.subheader(page_name)
st.markdown('---')

t1, t2 = st.tabs(['Single transaction', 'Input a table'])

with t1:
    st.markdown('**Enter a single transaction**')
    ranked_accounts = ss.accounts.sort_values(['AUTOMATED','RA_SCORE'], ascending=[True, False])['NAME']
    st.text_input('Description', key='description_input_home')
    c1, c2 = st.columns(2)
    with c1:
        st.number_input('Amount', key='amount_input_home')
        st.selectbox('Account', ranked_accounts, key='account_select_home')
    with c2:
        st.date_input('Date', key='date_input_home')
        st.selectbox('Category', ss.categories['NAME'], key='category_select_home')



    if ss.category_select_home == 'Transfer':
        c3, c4 = st.columns(2)
        with c3:
            st.selectbox('Account to/from:', ranked_accounts, key='transfer_account_name_home')

    st.button('Add transaction', key='add_transaction_button_home')

    st.write('''table below should show trans for that account/month, highlight any added, then not highlighted after push to db
            \n Also, drop to or from column and change other to "transfer account id"''')
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