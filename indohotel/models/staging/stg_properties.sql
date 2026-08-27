with source as (

    select * from {{ source('indohotel', 'properties') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source