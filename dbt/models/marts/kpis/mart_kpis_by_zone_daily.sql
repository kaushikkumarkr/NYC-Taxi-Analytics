with trips as (
    select * from {{ ref('fact_trips') }}
),

zones as (
    select * from {{ ref('dim_taxi_zone') }}
)

select
    trips.pickup_date,
    trips.pickup_location_id,
    zones.zone,
    
    count(*) as total_trips,
    sum(trips.total_amount) as total_revenue,
    avg(trips.trip_distance) as avg_distance,
    avg(trips.duration_seconds) / 60.0 as avg_duration_minutes

from trips
left join zones on trips.pickup_location_id = zones.location_id
group by 1, 2, 3
