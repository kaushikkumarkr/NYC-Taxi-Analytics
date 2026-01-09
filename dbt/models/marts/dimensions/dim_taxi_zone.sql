with staging as (
    select * from {{ ref('stg_taxi_zones') }}
)
select * from staging
