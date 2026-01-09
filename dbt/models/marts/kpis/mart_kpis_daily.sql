with trips as (
    select * from {{ ref('fact_trips') }}
)

select
    pickup_date,
    
    -- Volume
    count(*) as total_trips,
    
    -- Revenue & Efficiency
    sum(total_amount) as total_revenue,
    avg(fare_amount) as avg_fare,
    sum(total_amount) / nullif(sum(trip_distance), 0) as revenue_per_mile,
    sum(tip_amount) / nullif(sum(fare_amount), 0) as tip_rate,
    
    -- Operational
    avg(trip_distance) as avg_trip_distance,
    avg(duration_seconds) / 60.0 as avg_trip_duration_minutes,
    
    -- Load
    count(*) / 24.0 as trips_per_hour_avg,
    
    -- Dimensions/Mix
    sum(case when payment_type = 2 then 1 else 0 end)::numeric / nullif(count(*), 0) as pct_cash_trips,
    sum(case when congestion_surcharge > 0 then 1 else 0 end)::numeric / nullif(count(*), 0) as pct_congestion_trips,
    
    -- Late Night (10pm - 5am)
    sum(case when pickup_hour >= 22 or pickup_hour < 5 then 1 else 0 end)::numeric / nullif(count(*), 0) as late_night_share,
    
    -- Freshness
    max(pickup_datetime) as data_freshness_check_at

from trips
group by 1
order by 1 desc
