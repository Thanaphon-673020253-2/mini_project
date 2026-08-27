with source as (

    select * from {{ source('indohotel', 'fnb_transactions') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source