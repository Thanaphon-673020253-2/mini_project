with source as (

    select * from {{ source('indohotel', 'guests') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source