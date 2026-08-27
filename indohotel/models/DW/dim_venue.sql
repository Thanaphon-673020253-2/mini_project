select
    md5(cast(venue_id as string)) as venue_key,
    venue_id,
    venue_name,
    venue_type,
    max_capacity,
    cast(null as numeric) as area_sqm
from {{ ref('stg_venues') }}