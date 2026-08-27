with source as (

    select * from {{ source('indohotel', 'spa_bookings') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source