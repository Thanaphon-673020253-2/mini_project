with source as (

    select * from {{ source('indohotel', 'pricing_history') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source