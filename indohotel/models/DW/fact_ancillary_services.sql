WITH stg_spa_booking AS (

    SELECT 
        property_id,
        guest_id,
        NULL AS venue_id,
        NULL AS event_type_name,
        service_date AS booking_date,
        price AS spa_revenue,
        0 AS event_revenue,
        1 AS attendees

    FROM {{ ref('stg_spa_bookings') }}

),

stg_event_booking AS (

    SELECT
        property_id,
        NULL AS guest_id,
        venue_id,
        event_type AS event_type_name,
        event_date AS booking_date,
        0 AS spa_revenue,
        total_revenue AS event_revenue,
        capacity_booked AS attendees

    FROM {{ ref('stg_event_bookings') }}

),

combined_services AS (

    SELECT
        property_id,
        guest_id,
        venue_id,
        event_type_name,
        booking_date,
        spa_revenue,
        event_revenue,
        attendees

    FROM stg_spa_booking

    UNION ALL

    SELECT
        property_id,
        guest_id,
        venue_id,
        event_type_name,
        booking_date,
        spa_revenue,
        event_revenue,
        attendees

    FROM stg_event_booking

),

mapped_services AS (

    SELECT
        cs.property_id,
        cs.guest_id,
        cs.venue_id,
        cs.event_type_name,
        cs.booking_date,
        cs.spa_revenue,
        cs.event_revenue,
        cs.attendees,

        et.event_type_key

    FROM combined_services cs

    LEFT JOIN {{ ref('dim_event_type') }} et
        ON md5(
            COALESCE(
                LOWER(TRIM(cs.event_type_name)),
                'unknown'
            )
        ) = et.event_type_key

)

SELECT

    CAST(
        strftime(booking_date, '%Y%m%d')
        AS INTEGER
    ) AS date_key,

    md5(
        CAST(property_id AS VARCHAR)
    ) AS property_key,

    CASE
        WHEN guest_id IS NOT NULL
        THEN md5(CAST(guest_id AS VARCHAR))
        ELSE NULL
    END AS guest_key,

    CASE
        WHEN venue_id IS NOT NULL
        THEN md5(CAST(venue_id AS VARCHAR))
        ELSE NULL
    END AS venue_key,

    event_type_key,

    SUM(spa_revenue) AS spa_revenue,

    SUM(event_revenue) AS event_revenue,

    SUM(attendees) AS attendees_count

FROM mapped_services

GROUP BY
    1,
    2,
    3,
    4,
    5