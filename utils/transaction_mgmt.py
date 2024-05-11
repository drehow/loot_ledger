import utils.querying as q

def get_mat_table(end_date, account):
    start_date = end_date.replace(day=1).strftime('%Y-%m-%d')
    args = {
        0: start_date,
        1: end_date,
        2: account,
    }
    t1 = q.query('get_transactions_date_range', args)
    t1['FROM_DB'] = True
    return t1

def calc_month_stats(month_account_trans):
    stats = {
    'inflow': month_account_trans[
        (month_account_trans['AMOUNT'] > 0) & 
        ~(month_account_trans['CATEGORY'].isin(['Unknown transactions', 'Correction for Balance']))
        ]['AMOUNT'].sum(),
    'outflow': month_account_trans[
        (month_account_trans['AMOUNT'] <= 0) & 
        ~(month_account_trans['CATEGORY'].isin(['Unknown transactions', 'Correction for Balance']))
        ]['AMOUNT'].sum(),
    'correction': month_account_trans[
        (month_account_trans['CATEGORY'] == 'Correction for Balance')
        ]['AMOUNT'].sum(),
    'unknown': month_account_trans[
        (month_account_trans['CATEGORY'] == 'Unknown transactions')
        ]['AMOUNT'].sum(),
    }
    return stats