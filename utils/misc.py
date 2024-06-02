import pandas as pd
from datetime import datetime, timedelta

from streamlit import session_state as ss

def eom(date):
    return date.replace(day=pd.Timestamp(date).days_in_month)

def get_months_list():
    current_date = datetime.now()
    months_list = []
    while current_date >= datetime(2023, 1, 1):
        formatted_month = current_date.strftime("%b, %Y")
        months_list.append(formatted_month)
        current_date -= timedelta(days=current_date.day)
    return months_list