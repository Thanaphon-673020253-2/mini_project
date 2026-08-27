with source as (

    select * from {{ source('indohotel', 'financial_summary') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source