import pandas as pd
from datetime import datetime, timedelta

from streamlit import session_state as ss

def eom(date):
    return date.replace(day=pd.Timestamp(date).days_in_month)
def fom(date):
    return date.replace(day=1)

def get_months_list():
    current_date = datetime.now()
    months_list = []
    while current_date >= datetime(2023, 1, 1):
        formatted_month = current_date.strftime("%b, %Y")
        months_list.append(formatted_month)
        current_date -= timedelta(days=current_date.day)
    return months_list

def apply_changes_data_editor(df, changes):
   
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