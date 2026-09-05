WITH stg_bookings AS (
    SELECT * FROM {{ ref('stg_bookings') }}
),
dim_property AS (
    SELECT property_key, property_id FROM {{ ref('dim_property') }}
),
dim_guest AS (
    SELECT guest_key, guest_id FROM {{ ref('dim_guest') }}
),
dim_date AS (
    SELECT date_key, full_date FROM {{ ref('dim_date') }}
),
representative_rooms AS (
    SELECT 
        r.room_key,
        sr.property_id,
        sr.room_type,
        ROW_NUMBER() OVER (PARTITION BY sr.property_id, sr.room_type ORDER BY sr.room_id) as rn
    FROM {{ ref('stg_rooms') }} sr
    JOIN {{ ref('dim_room') }} r ON sr.room_id = r.room_id
)

SELECT
    b.booking_id,
    d.date_key,
    p.property_key,
    g.guest_key,
    rr.room_key,
    
    b.room_type,
    b.booking_channel,
    
    CAST(b.total_amount AS DOUBLE) AS booking_amount,
    0.0 AS discount_amount,
    CAST(b.total_amount AS DOUBLE) AS total_revenue,
    b.nights,
    1 AS room_count,
    
    DATE_DIFF('day', CAST(b.booking_date AS DATE), CAST(b.check_in_date AS DATE)) AS lead_time_days,
    
    CASE WHEN LOWER(b.status) IN ('cancelled', 'no-show') THEN TRUE ELSE FALSE END AS is_canceled,
    CASE WHEN LOWER(b.status) IN ('completed', 'checked-in') THEN TRUE ELSE FALSE END AS is_checked_in,
    
    b.ingestion_timestamp

FROM stg_bookings b
LEFT JOIN dim_date d ON CAST(b.check_in_date AS DATE) = d.full_date
LEFT JOIN dim_property p ON b.property_id = p.property_id
LEFT JOIN dim_guest g ON b.guest_id = g.guest_id
LEFT JOIN representative_rooms rr 
    ON b.property_id = rr.property_id 
    AND b.room_type = rr.room_type 
    AND rr.rn = 1