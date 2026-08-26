with stg_spa_booking as (
    select 
        property_id,
        guest_id,
        null as venue_id, -- ใน ERD spa_booking ไม่ได้เชื่อม venue_id
        service_date as booking_date,
        price as spa_revenue,
        1 as attendees
    from {{ ref('stg_spa_bookings') }}
),
stg_event_booking as (
    select
        property_id,
        null as guest_id,
        venue_id,
        event_date as booking_date,
        total_revenue as event_revenue,
        capacity_booked as attendees
    from {{ ref('stg_event_bookings') }}
),
combined_services as (
    select property_id, guest_id, venue_id, booking_date, spa_revenue, 0 as event_revenue, attendees from stg_spa_booking
    union all
    select property_id, guest_id, venue_id, booking_date, 0 as spa_revenue, event_revenue, attendees from stg_event_booking
)

select
    cast(strftime(booking_date, '%Y%m%d') as integer) as date_key,
    md5(cast(property_id as varchar)) as property_key,
    md5(cast(guest_id as varchar)) as guest_key,
    md5(cast(venue_id as varchar)) as venue_key,
    sum(spa_revenue) as spa_revenue,
    sum(event_revenue) as event_revenue,
    sum(attendees) as attendees_count
from combined_services
group by 1, 2, 3, 4