select
    booking_id,
    cast(strftime(check_in_date, '%Y%m%d') as integer) as date_key,
    md5(cast(property_id as varchar)) as property_key,
    md5(cast(guest_id as varchar)) as guest_key,
    md5(cast(room_type as varchar)) as room_key,
    (nights * room_rate) as booking_amount,
    ((nights * room_rate) - total_amount) as discount_amount,
    total_amount as total_revenue,
    nights,
    1 as room_count,
    date_diff('day', booking_date, check_in_date) as lead_time_days,
    case when status = 'Canceled' then true else false end as is_canceled,
    case when status in ('Checked In', 'Completed') then true else false end as is_checked_in
from {{ ref('stg_bookings') }}