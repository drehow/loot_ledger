import streamlit as st
from streamlit import session_state as ss
import pandas as pd

import utils.init as i
import utils.appearance as a

page_name = 'Account Table'
a.page_config(page_name)
i.init(page_name)
st.subheader(page_name)
st.markdown('---')

st.table(ss.accounts)

