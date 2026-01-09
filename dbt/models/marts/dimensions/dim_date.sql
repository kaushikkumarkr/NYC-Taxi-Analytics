-- In a real prod environment, use dbt_utils.date_spine
-- Here we generate a simple range for 2024-2025
with date_spine as (
    select 
        cast('2024-01-01' as date) + (n || ' days')::interval as date_day
    from generate_series(0, 365*2) n
)
select
    cast(date_day as date) as date_day,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    extract(quarter from date_day) as quarter,
    -- PostgreSQL specific day of week (0=Sunday, 6=Saturday)
    extract(dow from date_day) as day_of_week
from date_spine
