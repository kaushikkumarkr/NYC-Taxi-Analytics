# Sprint 2 Demo Script: Data Ingestion

**Estimated Time**: 2 minutes

## 1. Dev Mode Ingestion
"We will now ingest a sample of data to verify our pipeline logic."

```bash
make ingest-dev
```
*Wait for '✅ Loaded 100000 rows'*

## 2. Verify Data in Warehouse
"Let's confirm the data landed in Postgres."

```bash
docker compose exec postgres psql -U admin -d analytics -c "
SELECT count(*) as trip_count FROM raw.yellow_trips;
SELECT count(*) as zone_count FROM raw.taxi_zone_lookup;
"
```
*Expect: 100,000 trips and ~265 zones.*

## 3. Review Sample Data
"We can peek at the raw data:"

```bash
docker compose exec postgres psql -U admin -d analytics -c "
SELECT tpep_pickup_datetime, passenger_count, total_amount 
FROM raw.yellow_trips 
LIMIT 5;
"
```

## Conclusion
"Sprint 2 complete. We have a repeatable ingestion process for both Dev (sampled) and Prod (full) datasets."
