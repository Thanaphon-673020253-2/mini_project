with source as (

    select * from {{ source('indohotel', 'maintenance_tickets') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source