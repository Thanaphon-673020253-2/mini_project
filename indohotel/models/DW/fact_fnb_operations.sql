with stg_fnb_transactions as (
    select 
        t.*,
        o.property_id
    from {{ ref('stg_fnb_transactions') }} t
    left join {{ ref('stg_fnb_outlets') }} o
        on t.outlet_id = o.outlet_id
),
stg_fnb_waste_log as (
    select 
        w.outlet_id,
        cast(w.date as date) as waste_date,
        sum(w.quantity_wasted * coalesce(i.unit_cost, 0)) as total_waste_cost
    from {{ ref('stg_fnb_waste_log') }} w
    left join {{ ref('stg_fnb_inventory') }} i 
        on w.ingredient_id = i.ingredient_id
    group by 1, 2
)

select
    cast(format_date('%Y%m%d', cast(t.transaction_datetime as date)) as int64) as date_key,
    md5(cast(t.property_id as string)) as property_key,
    md5(cast(t.guest_id as string)) as guest_key,
    md5(cast(t.outlet_id as string)) as outlet_key,
    cast(null as string) as employee_key,
    t.total_price as sales_amount,
    (t.quantity * t.unit_price) as cost_of_goods_sold,
    coalesce(w.total_waste_cost, 0) as waste_cost,
    1 as transaction_count
from stg_fnb_transactions t
left join stg_fnb_waste_log w
    on t.outlet_id = w.outlet_id 
   and cast(t.transaction_datetime as date) = w.waste_date