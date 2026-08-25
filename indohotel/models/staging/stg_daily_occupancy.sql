with source as (

    select * from {{ source('indohotel', 'daily_occupancy') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source