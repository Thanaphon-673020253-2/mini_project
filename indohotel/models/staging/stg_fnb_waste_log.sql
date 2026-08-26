with source as (

    select * from {{ source('indohotel', 'fnb_waste_log') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source