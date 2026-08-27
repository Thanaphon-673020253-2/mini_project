with source as (

    select * from {{ source('indohotel', 'fnb_inventory') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source