.PHONY: help build up down clean ingest test setup ingest-dev dbt-check dbt-run dbt-docs alerts test-gx

help:
	@echo "Available commands:"
	@echo "  make setup    - Create venv and install dependencies"
	@echo "  make ingest   - Download and ingest 1 month of data (Jan 2024)"
	@echo "  make ingest-dev - Download, Sample (100k), and Ingest (Fast)"
	@echo "  make dbt-check - Check dbt connection"
	@echo "  make dbt-run  - Run dbt build"
	@echo "  make alerts   - Run anomaly detection"
	@echo "  make test-gx  - Run Great Expectations checks"
	@echo "  make build    - Build docker images"
	@echo "  make up       - Start all services (Postgres, Dagster, Superset)"
	@echo "  make down     - Stop all services"
	@echo "  make clean    - Stop services and remove volumes (RESET DATA)"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

clean:
	docker compose down -v

setup:
	python3 -m venv venv && . venv/bin/activate && pip install -e .

ingest:
	@echo "Downloading Jan 2024 data..."
	source venv/bin/activate && python scripts/download_tlc_parquet.py --months 2024-01
	source venv/bin/activate && python scripts/download_taxi_zones.py
	@echo "Loading data to Postgres..."
	source venv/bin/activate && python scripts/load_parquet_to_postgres.py --zones data/raw/taxi_zone_lookup.csv
	source venv/bin/activate && python scripts/load_parquet_to_postgres.py --file data/raw/yellow_tripdata_2024-01.parquet --table yellow_trips

ingest-dev:
	@echo "Running DEV MODE Ingestion..."
	source venv/bin/activate && python scripts/download_tlc_parquet.py --months 2024-01
	source venv/bin/activate && python scripts/download_taxi_zones.py
	@echo "Creating sample..."
	source venv/bin/activate && python scripts/make_dev_sample.py --input data/raw/yellow_tripdata_2024-01.parquet --output data/raw/yellow_tripdata_sample.parquet --rows 100000
	@echo "Loading sample to Postgres..."
	source venv/bin/activate && python scripts/load_parquet_to_postgres.py --zones data/raw/taxi_zone_lookup.csv
	source venv/bin/activate && python scripts/load_parquet_to_postgres.py --file data/raw/yellow_tripdata_sample.parquet --table yellow_trips

ingest-full:
	@echo "Running FULL PROD Ingestion (This may take a few minutes)..."
	source venv/bin/activate && python scripts/download_tlc_parquet.py --months 2024-01
	source venv/bin/activate && python scripts/download_taxi_zones.py
	@echo "Loading FULL Jan 2024 dataset..."
	source venv/bin/activate && python scripts/load_parquet_to_postgres.py --zones data/raw/taxi_zone_lookup.csv
	source venv/bin/activate && python scripts/load_parquet_to_postgres.py --file data/raw/yellow_tripdata_2024-01.parquet --table yellow_trips

dbt-check:
	source venv/bin/activate && cd dbt && dbt debug --profiles-dir .

dbt-run:
	source venv/bin/activate && cd dbt && dbt build --profiles-dir .

dbt-docs:
	source venv/bin/activate && cd dbt && dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .

alerts:
	source venv/bin/activate && PYTHONPATH=. python alerts/alert_runner.py

test-gx:
	source venv/bin/activate && python scripts/run_gx.py

forecast:
	@echo "Running Prophet Forecast..."
	source venv/bin/activate && python scripts/forecast_trips.py
