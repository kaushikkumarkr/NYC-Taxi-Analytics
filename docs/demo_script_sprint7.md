# Sprint 7 Demo Script: Great Expectations

**Estimated Time**: 2 minutes

## 1. Quality Check
"We have dbt tests for simple schema checks. Now we run Great Expectations for statistical validation and circuit breakers."

```bash
make test-gx
```
*Expect: "✅ Validation Success!"*

## 2. Simulate Bad Data (Integration Test)
"Let's break the rules. Revenue cannot be negative."

```bash
# Insert bad row
docker compose exec postgres psql -U admin -d analytics -c "
INSERT INTO dbt_dev_marts.mart_kpis_daily (pickup_date, total_revenue) 
VALUES ('2025-01-01', -100);
"

# Run Check
make test-gx
```
*Expect: "❌ Validation Failed!" and details about `expect_column_values_to_be_between` failure.*

## 3. Cleanup
```bash
docker compose exec postgres psql -U admin -d analytics -c "DELETE FROM dbt_dev_marts.mart_kpis_daily WHERE pickup_date = '2025-01-01';"
```

## Conclusion
"Sprint 7 complete. Our pipeline now has a rigid quality gate."
