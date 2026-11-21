select
    trip_id,
    "VendorID"                       as vendor_id,
    tpep_pickup_datetime::timestamp  as pickup_at,
    tpep_dropoff_datetime::timestamp as dropoff_at,
    "PULocationID"                   as pickup_location_id,
    "DOLocationID"                   as dropoff_location_id,
    passenger_count,
    trip_distance,
    fare_amount,
    total_amount,
    payment_type,
    pickup_month
from {{ source('staging', 'trips_silver') }}
