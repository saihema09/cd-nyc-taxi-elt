select
    trip_id,
    vendor_id,
    pickup_at,
    dropoff_at,
    pickup_location_id,
    dropoff_location_id,
    payment_type,
    passenger_count,
    trip_distance,
    fare_amount,
    total_amount,
    pickup_month
from {{ ref('stg_trips') }}
