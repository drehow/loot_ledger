import streamlit as st
from streamlit import session_state as ss

import pandas as pd
import os
import dotenv
import psycopg2

def set_conn():

    if ss['local_test']:
        dotenv.load_dotenv(override=True)
        params = {
            'dbname': os.environ.get('dbname'),
            'user': os.environ.get('user'),
            'password': os.environ.get('password'),
            'host': os.environ.get('host'),
        }
        conn = psycopg2.connect(**params)
    else:
        conn = st.connection("snowflake")

    return conn

def set_query_params(query_name, args = None):
    
    placeholder_mappings = {}
    if args:
        placeholder_mappings = {f'INSERT_{i+1}': value for i, value in enumerate(args.values())}
    with open(f'sql/{query_name}.sql','r') as file:
        query = file.read()
    params = []
    new_query = query 

    if ss['local_test']:
        replacers = '%s'
    else:
        replacers = '?'
    for placeholder, value in placeholder_mappings.items():
        if placeholder in query:
            new_query = new_query.replace(f"'{placeholder}'", replacers, 1)
            if value is not None:
                params.append(value)

    # st.write(enumerate(args))
    # st.write(placeholder_mappings)
    # st.write(new_query)
    # st.write(params)
    return new_query, params

@st.cache_data()
def query(name, args = {}):
    conn = set_conn()
    query, params = set_query_params(name, args)
    cursor = conn.cursor()
    cursor.execute(query, params)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    table = pd.DataFrame(results)
    table.columns = table.columns.str.upper()

    # guess you don't have to close conn with snowflake
    # conn.close()
    return table

