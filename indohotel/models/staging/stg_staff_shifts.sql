with source as (

    select * from {{ source('indohotel', 'staff_shifts') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source