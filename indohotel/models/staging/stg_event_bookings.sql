with source as (

    select * from {{ source('indohotel', 'event_bookings') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source