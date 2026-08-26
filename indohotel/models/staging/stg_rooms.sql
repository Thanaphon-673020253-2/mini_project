with source as (

    select * from {{ source('indohotel', 'rooms') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source