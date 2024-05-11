select t.date, t.amount, t.description, c.name as category
from fin.transaction t
left join fin.account a on a.id = t.account_id
left join fin.category c on c.id = t.category_id
where DATE between 
'INSERT_1' 
and
'INSERT_2' 
and a.name = 
'INSERT_3'
--'Discover Checking'
order by Date desc;