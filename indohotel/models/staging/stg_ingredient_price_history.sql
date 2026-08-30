with source as (

    select * from {{ source('indohotel', 'ingredient_price_history') }}
)
select
    *,
    current_localtimestamp() as ingestion_timestamp
from source