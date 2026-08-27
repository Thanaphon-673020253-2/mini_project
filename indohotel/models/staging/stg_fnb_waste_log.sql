with source as (

    select * from {{ source('indohotel', 'fnb_waste_log') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source