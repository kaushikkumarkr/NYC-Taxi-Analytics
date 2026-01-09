# Sprint 3 Demo Script: dbt Transformations

**Estimated Time**: 2 minutes

## 1. Run dbt Build
"We will now run the transformation layer. This compiles our SQL code, runs it against Postgres, and executes data quality tests."

```bash
make dbt-run
```
*Wait for "Completed successfully"*

## 2. Verify Lineage
"This built the following lineage:"
- `raw.yellow_trips` -> `stg_yellow_trips` -> `fact_trips`
- `raw.taxi_zone_lookup` -> `stg_taxi_zones` -> `dim_taxi_zone`

## 3. Examine Data Quality
"We ran 12 data quality (DQ) tests. For example, we verified:"
- `fact_trips` has valid relationships to `dim_taxi_zone`.
- `payment_type` only contains valid codes (0-6).
- Primary keys are unique and not null.

## 4. Check the Data
```bash
docker compose exec postgres psql -U admin -d analytics -c "
SELECT count(*) FROM dbt_dev_marts.fact_trips;
SELECT pickup_datetime, trip_distance, fare_amount 
FROM dbt_dev_marts.fact_trips 
ORDER BY pickup_datetime DESC LIMIT 5;
"
```

## Conclusion
"Sprint 3 complete. We have a trusted, tested Fact table ready for KPI aggregation."
