with source as (

    select * from {{ source('indohotel', 'venues') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source