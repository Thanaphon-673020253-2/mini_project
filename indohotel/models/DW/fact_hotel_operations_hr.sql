with stg_payroll as (
    select 
        p.*,
        e.property_id
    from {{ ref('stg_payroll') }} p
    left join {{ ref('stg_employees') }} e 
        on p.employee_id = e.employee_id
),
stg_employee_performance as (
    select * from {{ ref('stg_employee_performance') }}
),
stg_maintenance_tickets as (
    select 
        property_id,
        assigned_staff_id,
        room_id,
        cast(reported_date as date) as ticket_date,
        sum(cost) as total_maintenance_cost,
        count(ticket_id) as ticket_count
    from {{ ref('stg_maintenance_tickets') }}
    group by 1, 2, 3, 4
)

select
    cast(format_date('%Y%m%d', coalesce(m.ticket_date, current_date())) as int64) as date_key,
    md5(cast(coalesce(m.property_id, p.property_id) as string)) as property_key,
    md5(cast(coalesce(m.assigned_staff_id, p.employee_id) as string)) as employee_key,
    md5(cast(m.room_id as string)) as room_key,
    coalesce(p.net_salary, 0) as payroll_amount,
    perf.score as performance_score,
    coalesce(m.total_maintenance_cost, 0) as maintenance_cost,
    coalesce(m.ticket_count, 0) as maintenance_ticket_count
from stg_payroll p
full outer join stg_maintenance_tickets m
    on p.employee_id = m.assigned_staff_id
   and p.property_id = m.property_id
left join stg_employee_performance perf
    on coalesce(m.assigned_staff_id, p.employee_id) = perf.employee_id