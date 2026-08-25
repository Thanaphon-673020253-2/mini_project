with source as (

    select * from {{ source('indohotel', 'bookings') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source