with source as (

    select * from {{ source('indohotel', 'fnb_outlets') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source