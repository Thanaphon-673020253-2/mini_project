select

    md5(cast(guest_id as varchar)) as guest_key,

    guest_id,

    full_name,

    nationality,

    case
        when upper(trim(nationality)) = 'INDONESIA' then true
        else false
    end as is_domestic,

    loyalty_tier,

    registered_date

from {{ ref('stg_guests') }}