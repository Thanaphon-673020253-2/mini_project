with source as (

    select * from {{ source('indohotel', 'event_bookings') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source