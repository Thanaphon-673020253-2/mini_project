select
    md5(cast(room_id as string)) as room_key,
    room_id,
    room_number,
    room_type,
    floor
from {{ ref('stg_rooms') }}