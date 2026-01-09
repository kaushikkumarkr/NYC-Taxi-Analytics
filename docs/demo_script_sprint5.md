# Sprint 5 Demo Script: Anomaly Detection

**Estimated Time**: 2 minutes

## 1. Unit Testing the Math
"We implemented a robust Z-score and Day-of-Week anomaly detector. Let's verify the logic with unit tests."

```bash
source venv/bin/activate
python tests/test_anomaly.py
```
*Expect: Validated Z-Score Spike, Z-Score Stable, and DoW Baseline.*

## 2. Running Detection on Real Data
"Now we scan our Aggregation Marts for anomalies."

```bash
make alerts
```
*Likely no anomalies if data is clean, or some if the distribution is erratic.*

## 3. Inspecting Alerts
"If alerts were found, they land in the `kpi_alerts` table."

```bash
docker compose exec postgres psql -U admin -d analytics -c "
SELECT alert_date, metric_name, method, round(deviation_pct, 2) as deviation, severity 
FROM kpi_alerts 
ORDER BY alert_date DESC;
"
```

## Conclusion
"Sprint 5 complete. We have an automated Reliability Engine that continuously monitors our KPIs."
