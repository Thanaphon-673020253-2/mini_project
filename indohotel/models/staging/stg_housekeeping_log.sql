with source as (

    select * from {{ source('indohotel', 'housekeeping_log') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source