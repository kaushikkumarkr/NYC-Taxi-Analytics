# Sprint 4 Demo Script: KPI Marts

**Estimated Time**: 2 minutes

## 1. Build Metrics Layer
"We will now build the aggregation layer (Marts) which powers our dashboards and alerting."

```bash
make dbt-run
```
*Wait for "Completed successfully" (20 tests passed)*

## 2. Inspect Daily KPIs
"Let's look at the core `mart_kpis_daily` table."

```bash
docker compose exec postgres psql -U admin -d analytics -c "
SELECT 
    pickup_date, 
    total_trips, 
    round(total_revenue, 2) as revenue, 
    round(avg_fare, 2) as avg_fare,
    round(late_night_share, 2) as late_night_pct
FROM dbt_dev_marts.mart_kpis_daily
ORDER BY pickup_date DESC
LIMIT 5;
"
```
*Show the daily rollout of metrics.*

## 3. Drill Down by Zone
"We can also see performance by Zone."

```bash
docker compose exec postgres psql -U admin -d analytics -c "
SELECT 
    dz.zone, 
    k.total_trips, 
    round(k.avg_duration_minutes, 1) as duration_min 
FROM dbt_dev_marts.mart_kpis_by_zone_daily k
JOIN dbt_dev_marts.dim_taxi_zone dz ON k.pickup_location_id = dz.location_id
WHERE k.pickup_date = '2024-01-15'
ORDER BY k.total_trips DESC
LIMIT 5;
"
```

## Conclusion
"Sprint 4 complete. We have a robust, tested metrics layer ready for the Anomaly Detection Engine."
