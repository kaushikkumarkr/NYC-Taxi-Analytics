# Sprint 6 Demo Script: Root Cause Investigation

**Estimated Time**: 3 minutes

## 1. Simulate a Crash
"To test our investigation engine, we will simulate a catastrophic drop in trips for tomorrow."

```bash
docker compose exec postgres psql -U admin -d analytics -c "
INSERT INTO dbt_dev_marts.mart_kpis_daily (pickup_date, total_trips, total_revenue, avg_fare, avg_trip_distance, avg_trip_duration_minutes, trips_per_hour_avg, pct_cash_trips, pct_card_trips, late_night_share, data_freshness_check_at)
VALUES ('2024-02-01', 10, 500, 50, 2.5, 10, 0.5, 0.1, 0.9, 0.2, NOW());
"
```

## 2. Run the Investigation
"Run the detection & investigation engine."

```bash
make alerts
```
*Expect: "🚨 ALERT FOUND" followed by "🕵️ running Root Cause Analysis" and "✅ Drivers Saved."*

## 3. View the Results
"Let's ask: WHY did trips drop? Which zones were responsible?"

```bash
docker compose exec postgres psql -U admin -d analytics -c "
SELECT 
    a.metric_name,
    a.deviation_pct,
    d.dimension,
    d.segment_value,
    round(d.delta, 0) as drop_amount,
    round(d.contribution_pct, 2) as contrib
FROM kpi_alert_drivers d
JOIN kpi_alerts a ON d.alert_id = a.alert_id
WHERE a.alert_date = '2024-02-01'
ORDER BY a.metric_name, d.delta ASC
LIMIT 10;
"
```
*Expect to see top zones (like JFK, Midtown) listed as the biggest losers.*

## 4. Cleanup
```bash
docker compose exec postgres psql -U admin -d analytics -c "DELETE FROM dbt_dev_marts.mart_kpis_daily WHERE pickup_date = '2024-02-01';"
```

## Conclusion
"Sprint 6 complete. The system now automatically identifies WHY an anomaly occurred."
