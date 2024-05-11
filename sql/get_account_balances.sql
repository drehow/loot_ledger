select date, a.name as NAME, ab.balance as BALANCE
from fin.account_balance ab
left join fin.account a on a.id = ab.account_id