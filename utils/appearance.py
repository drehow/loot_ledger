import streamlit as st
from streamlit import session_state as ss
import streamlit.components.v1 as components

import pandas as pd

def page_config(title):
    st.set_page_config(
        layout = "wide",
        page_title = title,
        page_icon = ":spy:",
        initial_sidebar_state= 'collapsed',
    )

def css():
    st.markdown("""
    <style>
        .{table_id} thead th {{
            background-color: #4CAF50; /* Change this to your desired color */
            color: white;
        }}
    </style>
    """, unsafe_allow_html=True)
    return

if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

def ColourWidgetText(wgt_txt, wch_colour = '#000000'):
    htmlstr = """<script>var elements = window.parent.document.querySelectorAll('*'), i;
                for (i = 0; i < elements.length; ++i) { if (elements[i].innerText == |wgt_txt|) 
                    elements[i].style.color = ' """ + wch_colour + """ '; } </script>  """

    htmlstr = htmlstr.replace('|wgt_txt|', "'" + wgt_txt + "'")
    components.html(f"{htmlstr}", height=0, width=0)

def prettyMetric(text, value, color = '#000000'):
    st.metric(text, f"{round(value,0):,}")
    # if round(value,0) != 0:
    #     ColourWidgetText(text, color) 
    #     ColourWidgetText(f"{round(value,0):,}", color) 

def table_css(table_id='custom_table'):
    return f"""
<style>
    .{table_id} {{
        width: 100%;
    }}
    .{table_id} thead th {{
        background-color: #4CAF50; /* Change this to your desired color */
        color: white;
    }}
    .{table_id} tbody tr:nth-child(even) {{
        background-color: #000000; /* Optional: style alternating row colors */
    }}
    .{table_id} tbody tr:nth-child(odd) {{
        background-color: #000000; /* Optional: style alternating row colors */
    }}
</style>
"""
def style_mat_table(df):
    sdf = df.copy()
    highlight_mask = sdf['FROM_DB'] == False
    sdf['AMOUNT'] = sdf['AMOUNT'].apply(lambda x: f"({round(abs(x),0):,})" if x < 0 else f"{round(x,0):,}")
    sdf['DATE'] = pd.to_datetime(sdf['DATE']).dt.strftime('%Y-%m-%d')
    sdf = sdf[['DATE', 'DESCRIPTION', 'AMOUNT', 'CATEGORY']]
    sdf = sdf.style.set_properties(subset=['AMOUNT'], **{'text-align': 'right'})

    # highlight rows where FROM_DB is False
    sdf = sdf.apply(lambda x: ['background-color: #657d8a' if highlight_mask[x.name] else '' for _ in x], axis=1)

    # Convert styled DataFrame to HTML and manually add the class
    df_html = sdf.hide(axis='index').to_html().replace('<table', '<table class="custom_table"')

    # Render the styled HTML in Streamlit with the custom CSS
    return st.markdown(table_css('custom_table') + df_html, unsafe_allow_html=True)


