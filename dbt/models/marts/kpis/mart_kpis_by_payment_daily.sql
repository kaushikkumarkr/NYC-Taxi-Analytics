with trips as (
    select * from {{ ref('fact_trips') }}
)

select
    pickup_date,
    payment_type,
    
    count(*) as total_trips,
    avg(fare_amount) as avg_fare,
    sum(total_amount) as total_revenue

from trips
group by 1, 2
