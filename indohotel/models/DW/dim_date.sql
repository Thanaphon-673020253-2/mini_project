with date_range as (
    select date_day
    from unnest(generate_date_array(cast('2020-01-01' as date), cast('2030-12-31' as date), interval 1 day)) as date_day
)

select
    cast(format_date('%Y%m%d', date_day) as int64) as date_key,
    date_day as full_date,
    format_date('%A', date_day) as day_of_week,
    format_date('%B', date_day) as month_name,
    concat('Q', extract(quarter from date_day)) as quarter,
    extract(year from date_day) as year,
    case when extract(dayofweek from date_day) in (1, 7) then true else false end as is_weekend,
    case 
        when extract(month from date_day) in (11, 12, 1, 2) then 'High Season'
        when extract(month from date_day) in (6, 7, 8) then 'Peak Season'
        else 'Low Season'
    end as season
from date_range