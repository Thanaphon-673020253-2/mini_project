with source as (

    select * from {{ source('indohotel', 'employee_performance') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source