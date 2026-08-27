with source as (

    select * from {{ source('indohotel', 'recipe_bom') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source