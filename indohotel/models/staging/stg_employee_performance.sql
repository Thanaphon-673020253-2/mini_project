with source as (

    select * from {{ source('indohotel', 'employee_performance') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source