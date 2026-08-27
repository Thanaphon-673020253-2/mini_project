with source as (

    select * from {{ source('indohotel', 'daily_occupancy') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source