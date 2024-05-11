import pandas as pd

def eom(date):
    return date.replace(day=pd.Timestamp(date).days_in_month)