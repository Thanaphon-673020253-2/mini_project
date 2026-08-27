select
    md5(cast(employee_id as string)) as employee_key,
    employee_id,
    full_name,
    role_title,
    department
from {{ ref('stg_employees') }}