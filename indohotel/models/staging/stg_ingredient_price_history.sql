with source as (

    select * from {{ source('indohotel', 'ingredient_price_history') }}
)
select
    *,
    current_timestamp() as ingestion_timestamp
from source