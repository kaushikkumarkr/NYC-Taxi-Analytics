# Sprint 1 Demo Script: Foundation & Infrastructure

**Estimated Time**: 2 minutes

## 1. Setup & Ingestion
"We have established the local production-grade environment. I'll show how easy it is to spin up the stack."

```bash
# Show the clean state
make clean

# Spin up the infrastructure
make up
```
*Wait for services to stabilize (approx 10-20s)*

## 2. Infrastructure verification
"We have 3 core services running in Docker:"
1. **Postgres (Warehouse)**: The central data store.
2. **Dagster (Orchestration)**: managing our pipelines.
3. **Superset (BI)**: for our dashboards.

```bash
docker ps
```
*Show the 4 containers: warehouse_pg, dagster_daemon, dagster_webserver, superset.*

## 3. Connectivity Check
"Let's verify they are responsive."

**Dagster**:
Open [localhost:3000](http://localhost:3000).
"This is our orchestration layer. It's empty now, but ready for assets."

**Superset**:
Open [localhost:8088](http://localhost:8088).
"Log in with `admin/admin`. We have a running BI instance connected to our network."

**Database**:
"We verified the database is initialized with our schemas."
```bash
docker compose exec postgres psql -U admin -d analytics -c "\dt"
```
*Show 'No relations found' (which is expected) but schemas exist.*

## Conclusion
"Sprint 1 is complete. We have a reproducible, containerized foundation ready for data."
