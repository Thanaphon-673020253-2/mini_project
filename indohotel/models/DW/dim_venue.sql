select
    md5(cast(venue_id as varchar)) as venue_key,
    venue_id,
    venue_name,
    venue_type,
    max_capacity,
    null as area_sqm
from {{ ref('stg_venues') }}