import streamlit as st
from streamlit import session_state as ss
import pandas as pd

import utils.init as i
import utils.appearance as a

a.page_config('Home')
i.init('Home')

st.table(ss.accounts)

# Initialize connection.
# conn = st.connection("snowflake")

# Perform query.
# df = conn.query("SELECT * from fin.category;", ttl=600)


# Print results.
# for row in df.itertuples():
#     st.write(f"{row.NAME} has a {row.ID}")


# st.subheader('holy shit we are connected to a cloud snowflake database that is awesome')