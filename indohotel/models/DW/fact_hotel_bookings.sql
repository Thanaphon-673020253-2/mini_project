select
    booking_id,
    cast(format_date('%Y%m%d', cast(check_in_date as date)) as int64) as date_key,
    md5(cast(property_id as string)) as property_key,
    md5(cast(guest_id as string)) as guest_key,
    md5(cast(room_type as string)) as room_key,
    (nights * room_rate) as booking_amount,
    ((nights * room_rate) - total_amount) as discount_amount,
    total_amount as total_revenue,
    nights,
    1 as room_count,
    date_diff(cast(check_in_date as date), cast(booking_date as date), day) as lead_time_days,
    case when status = 'Canceled' then true else false end as is_canceled,
    case when status in ('Checked In', 'Completed') then true else false end as is_checked_in
from {{ ref('stg_bookings') }}