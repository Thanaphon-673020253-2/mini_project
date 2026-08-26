with source as (

    select * from {{ source('indohotel', 'payroll') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source