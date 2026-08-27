with source as (

    select * from {{ source('indohotel', 'fnb_outlets') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source