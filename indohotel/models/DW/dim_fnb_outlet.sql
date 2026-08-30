select
    md5(cast(outlet_id as varchar)) as outlet_key,
    outlet_id,
    outlet_name,
    outlet_type,
    property_id
from {{ ref('stg_fnb_outlets') }}