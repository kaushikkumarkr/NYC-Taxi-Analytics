with source as (
    select * from {{ source('raw', 'taxi_zone_lookup') }}
),

renamed as (
    select
        cast("LocationID" as integer) as location_id,
        "Borough" as borough,
        "Zone" as zone,
        "service_zone" as service_zone
    from source
)

select * from renamed
