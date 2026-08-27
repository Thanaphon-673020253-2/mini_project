with source as (

    select * from {{ source('indohotel', 'bookings') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source