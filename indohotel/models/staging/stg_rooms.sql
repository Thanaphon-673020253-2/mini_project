with source as (

    select * from {{ source('indohotel', 'rooms') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source