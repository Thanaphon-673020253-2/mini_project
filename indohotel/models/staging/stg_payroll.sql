with source as (

    select * from {{ source('indohotel', 'payroll') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source