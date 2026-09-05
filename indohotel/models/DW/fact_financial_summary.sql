WITH stg_financial AS (
    SELECT * FROM {{ ref('stg_financial_summary') }}
),
dim_property AS (
    SELECT property_key, property_id FROM {{ ref('dim_property') }}
),
dim_date AS (
    SELECT date_key, full_date FROM {{ ref('dim_date') }}
)

SELECT
    -- แปลง period '2023-07' ให้กลายเป็น '2023-07-01' (วันที่ 1 ของเดือน) เพื่อเชื่อมกับ dim_date
    d.date_key,
    p.property_key,
    
    -- Degenerate Dimension
    f.department,
    
    -- Facts / Metrics
    CAST(f.departmental_revenue AS DOUBLE) AS departmental_revenue,
    CAST(f.departmental_expense AS DOUBLE) AS departmental_expense,
    CAST(f.departmental_profit AS DOUBLE) AS departmental_profit,
    CAST(f.undistributed_expense AS DOUBLE) AS undistributed_expense,
    CAST(f.gop AS DOUBLE) AS gop,
    
    f.ingestion_timestamp

FROM stg_financial f
-- เชื่อม Date โดยการต่อ String '-01' เข้าไปที่ท้าย period
LEFT JOIN dim_date d ON CAST(f.period || '-01' AS DATE) = d.full_date
LEFT JOIN dim_property p ON f.property_id = p.property_id