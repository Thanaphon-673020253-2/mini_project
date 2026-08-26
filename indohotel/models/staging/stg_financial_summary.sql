with source as (

    select * from {{ source('indohotel', 'financial_summary') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source