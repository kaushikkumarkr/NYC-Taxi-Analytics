with trips as (
    select * from {{ ref('stg_yellow_trips') }}
),
dim_date as (
    select * from {{ ref('dim_date') }}
)

select
    -- Surrogate Key (Optional, depending on style. MD5 of keys is common)
    -- md5(cast(vendor_id as varchar) || cast(pickup_datetime as varchar)) as trip_sk,
    
    trips.vendor_id,
    trips.pickup_location_id,
    trips.dropoff_location_id,
    
    trips.pickup_datetime,
    trips.dropoff_datetime,
    
    -- Date/Time Dimensions
    cast(trips.pickup_datetime as date) as pickup_date,
    extract(hour from trips.pickup_datetime) as pickup_hour,
    
    -- Metrics
    trips.passenger_count,
    trips.trip_distance,
    trips.fare_amount,
    trips.extra,
    trips.mta_tax,
    trips.tip_amount,
    trips.tolls_amount,
    trips.improvement_surcharge,
    trips.congestion_surcharge,
    trips.total_amount,
    trips.payment_type,
    
    -- Derived Metrics
    extract(epoch from (trips.dropoff_datetime - trips.pickup_datetime)) as duration_seconds,
    
    case 
        when extract(epoch from (trips.dropoff_datetime - trips.pickup_datetime)) > 0 
        then trips.trip_distance / (extract(epoch from (trips.dropoff_datetime - trips.pickup_datetime)) / 3600)
        else 0
    end as avg_speed_mph

from trips
where trips.pickup_datetime IS NOT NULL
