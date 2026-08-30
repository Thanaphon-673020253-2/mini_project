with source as (

    select * from {{ source('indohotel', 'role_permissions') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source