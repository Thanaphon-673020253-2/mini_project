select
    md5(cast(property_id as string)) as property_key,
    property_id,
    property_name,
    city,
    region,
    star_rating,
    total_rooms
from {{ ref('stg_properties') }}