# Operational Runbook: Analytics Reliability Command Center

**System Owner**: Analytics Engineering Team
**On-Call**: `admin@example.com`

## 1. Daily Workflow (The "Happy Path")
Every morning (at 08:00 UTC), the pipeline should run:

```bash
# 1. Ingest latest data (Simulated)
make ingest

# 2. Run dbt Transformations
make dbt-run

# 3. Validate Data Quality
make test-gx

# 4. Detect Anomalies
make alerts
```

## 2. Incident Response (The "Sad Path")

### Scenario A: `make test-gx` fails
**Symptom**: Pipeline exit code 1. "Validation Failed".
**Triage**:
1. Check `gx/uncommitted/data_docs/local_site/index.html` for the failed expectation.
2. If it's a Volume issue (0 rows): Check upstream API availability.
3. If it's Integrity (Negative Revenue): Check `raw.yellow_trips` for bad data.
   ```sql
   SELECT * FROM raw.yellow_trips WHERE total_amount < 0;
   ```

### Scenario B: Anomaly Detected
**Symptom**: Slack alert (simulated via log) from `make alerts`.
**Triage**:
1. Run the RCA tool manually to see drivers:
   ```bash
   make alerts
   ```
2. Check `kpi_alert_drivers` table for root cause.
3. If valid anomaly (e.g., Blizzard in NY), acknowledge and annotate.
4. If invalid (Data issue), see Scenario A.

## 3. Disaster Recovery
**Problem**: Database corrupted or deleted.
**Recovery**:
```bash
# 1. Nuke everything
make down
docker volume rm analytics-command-center_postgres_data

# 2. Rebuild
make up
make setup
make ingest-dev # Load Jan 2024 sample
make dbt-run
```
