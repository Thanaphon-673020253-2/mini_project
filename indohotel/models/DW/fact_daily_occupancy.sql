WITH stg_occupancy AS (
    SELECT * FROM {{ ref('stg_daily_occupancy') }}
),
dim_property AS (
    SELECT property_key, property_id FROM {{ ref('dim_property') }}
),
dim_date AS (
    SELECT date_key, full_date FROM {{ ref('dim_date') }}
)

SELECT
    -- Surrogate Keys
    d.date_key,
    p.property_key,
    
    -- Degenerate Dimension
    o.room_type,
    
    -- Facts / Metrics
    CAST(o.rooms_sold AS INTEGER) AS rooms_sold,
    CAST(o.total_rooms_available AS INTEGER) AS total_rooms_available,
    CAST(o.occupancy_rate AS DOUBLE) AS occupancy_rate,
    CAST(o.adr AS DOUBLE) AS adr,
    CAST(o.revpar AS DOUBLE) AS revpar,
    
    o.ingestion_timestamp

FROM stg_occupancy o
LEFT JOIN dim_date d ON CAST(o.date AS DATE) = d.full_date
LEFT JOIN dim_property p ON o.property_id = p.property_id