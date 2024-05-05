import streamlit as st
import pandas as pd


# Initialize connection.
conn = st.connection("snowflake")

# Perform query.
df = conn.query("SELECT * from fin.account;", ttl=600)

# Print results.
for row in df.itertuples():
    st.write(f"{row.NAME} has a :{row.ID}:")