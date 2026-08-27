with source as (

    select * from {{ source('indohotel', 'pricing_history') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source