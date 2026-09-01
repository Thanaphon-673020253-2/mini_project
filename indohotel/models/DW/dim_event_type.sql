-- models/DW/dim_event_type.sql
WITH source_data AS (
    SELECT DISTINCT
        -- สร้าง Primary Key ด้วย Hashing หากใน Staging ยังไม่มี Key
        md5(COALESCE(LOWER(TRIM(event_type)), 'unknown')) AS event_type_key,
        event_type AS event_type_name
    FROM {{ ref('stg_event_bookings') }}
    WHERE event_type IS NOT NULL
)

SELECT 
    event_type_key,
    event_type_name
FROM source_data