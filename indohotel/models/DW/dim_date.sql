with date_range as (
    select range::date as date_day
    from range(date '2020-01-01', date '2031-01-01', interval 1 day)
)

select
    cast(strftime(date_day, '%Y%m%d') as integer) as date_key,
    date_day as full_date,
    strftime(date_day, '%A') as day_of_week,
    strftime(date_day, '%B') as month_name,
    'Q' || extract(quarter from date_day) as quarter,
    extract(year from date_day) as year,
    case when extract(dayofweek from date_day) in (0, 6) then true else false end as is_weekend,
    case 
        when extract(month from date_day) in (11, 12, 1, 2) then 'High Season'
        when extract(month from date_day) in (6, 7, 8) then 'Peak Season'
        else 'Low Season'
    end as season
from date_range