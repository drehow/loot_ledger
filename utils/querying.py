import streamlit as st
import pandas as pd

def set_conn():
    return st.connection("snowflake")

def set_query_params(query_name, args = None):
    
    placeholder_mappings = {}
    if len(args) > 0:
        placeholder_mappings = {
            'INSERT_DATE': args[0],
        }
        
    with open(f'sql/{query_name}.sql','r') as file:
        query = file.read()
    params = []
    new_query = query
    for placeholder, value in placeholder_mappings.items():
        if placeholder in query:
            new_query = new_query.replace(f"'{placeholder}'", '?', 1)
            if value is not None:
                params.append(value)
    
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
    
    # guess you don't have to close conn with snowflake
    # conn.close()
    return table

