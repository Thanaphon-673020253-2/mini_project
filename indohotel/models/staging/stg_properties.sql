with source as (

    select * from {{ source('indohotel', 'properties') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source