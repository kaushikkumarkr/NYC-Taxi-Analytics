with trips as (
    select * from {{ ref('fact_trips') }}
)

select
    pickup_date,
    
    -- Volume
    count(*) as total_trips,
    
    -- Revenue
    sum(total_amount) as total_revenue,
    avg(fare_amount) as avg_fare,
    avg(tip_amount) as avg_tip,
    
    -- Operational
    avg(trip_distance) as avg_trip_distance,
    avg(duration_seconds) / 60.0 as avg_trip_duration_minutes,
    
    -- Load/Utilization
    count(*) / 24.0 as trips_per_hour_avg,
    
    -- Dimensions/Mix
    sum(case when payment_type = 2 then 1 else 0 end)::numeric / nullif(count(*), 0) as pct_cash_trips,
    sum(case when payment_type = 1 then 1 else 0 end)::numeric / nullif(count(*), 0) as pct_card_trips,
    
    -- Late Night (10pm - 5am)
    sum(case when pickup_hour >= 22 or pickup_hour < 5 then 1 else 0 end)::numeric / nullif(count(*), 0) as late_night_share,
    
    -- Freshness
    max(pickup_datetime) as data_freshness_check_at

from trips
group by 1
order by 1 desc
