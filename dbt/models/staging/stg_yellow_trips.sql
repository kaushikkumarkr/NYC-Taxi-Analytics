with source as (
    select * from {{ source('raw', 'yellow_trips') }}
),

renamed as (
    select
        -- Identifiers
        cast(vendorid as integer) as vendor_id,
        cast(pulocationid as integer) as pickup_location_id,
        cast(dolocationid as integer) as dropoff_location_id,
        
        -- Timestamps
        cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
        cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
        
        -- Trip info
        cast(passenger_count as integer) as passenger_count,
        cast(trip_distance as numeric) as trip_distance,
        cast(store_and_fwd_flag as varchar) as store_and_fwd_flag,
        cast(ratecodeid as integer) as rate_code_id,
        
        -- Payment
        cast(payment_type as integer) as payment_type,
        cast(fare_amount as numeric) as fare_amount,
        cast(extra as numeric) as extra,
        cast(mta_tax as numeric) as mta_tax,
        cast(tip_amount as numeric) as tip_amount,
        cast(tolls_amount as numeric) as tolls_amount,
        cast(improvement_surcharge as numeric) as improvement_surcharge,
        cast(total_amount as numeric) as total_amount,
        cast(congestion_surcharge as numeric) as congestion_surcharge,
        cast(airport_fee as numeric) as airport_fee

    from source
)

select * from renamed
where pickup_datetime >= '2000-01-01' -- Basic sanity filter
