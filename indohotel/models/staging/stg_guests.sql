with source as (

    select * from {{ source('indohotel', 'guests') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source