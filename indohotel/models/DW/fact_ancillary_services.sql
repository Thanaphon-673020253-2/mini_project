with stg_spa_booking as (
    select 
        property_id,
        cast(guest_id as string) as guest_id,
        'SPA_FACILITY' as venue_id,
        cast(service_date as date) as booking_date,
        price as spa_revenue,
        1 as attendees
    from {{ ref('stg_spa_bookings') }}
),
stg_event_booking as (
    select
        property_id,
        cast(null as string) as guest_id,
        cast(venue_id as string) as venue_id,
        cast(event_date as date) as booking_date,
        total_revenue as event_revenue,
        capacity_booked as attendees
    from {{ ref('stg_event_bookings') }}
),
combined_services as (
    select property_id, guest_id, venue_id, booking_date, spa_revenue, 0.0 as event_revenue, attendees from stg_spa_booking
    union all
    select property_id, guest_id, venue_id, booking_date, 0.0 as spa_revenue, event_revenue, attendees from stg_event_booking
)

select
    cast(format_date('%Y%m%d', booking_date) as int64) as date_key,
    md5(cast(property_id as string)) as property_key,
    md5(cast(guest_id as string)) as guest_key,
    md5(cast(venue_id as string)) as venue_key,
    sum(spa_revenue) as spa_revenue,
    sum(event_revenue) as event_revenue,
    sum(attendees) as attendees_count
from combined_services
group by 1, 2, 3, 4