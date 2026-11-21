select distinct
    pickup_at::date                as date_day,
    extract(year from pickup_at)   as year,
    extract(month from pickup_at)  as month,
    extract(day from pickup_at)    as day,
    extract(dow from pickup_at)    as day_of_week
from {{ ref('stg_trips') }}
