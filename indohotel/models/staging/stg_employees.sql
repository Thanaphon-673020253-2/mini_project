with source as (

    select * from {{ source('indohotel', 'employees') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source