with trips as (
    select * from {{ ref('fact_trips') }}
)

select
    pickup_date,
    pickup_hour,
    
    count(*) as total_trips,
    sum(total_amount) as total_revenue,
    avg(fare_amount) as avg_fare,
    avg(trip_distance) as avg_distance

from trips
group by 1, 2
order by 1 desc, 2 asc
