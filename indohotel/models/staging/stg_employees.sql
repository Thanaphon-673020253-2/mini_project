with source as (

    select * from {{ source('indohotel', 'employees') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source