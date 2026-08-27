with source as (

    select * from {{ source('indohotel', 'housekeeping_log') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source