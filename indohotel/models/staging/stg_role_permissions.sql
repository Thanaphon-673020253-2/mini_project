with source as (

    select * from {{ source('indohotel', 'role_permissions') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source