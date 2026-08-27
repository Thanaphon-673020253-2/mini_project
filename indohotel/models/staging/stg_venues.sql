with source as (

    select * from {{ source('indohotel', 'venues') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source