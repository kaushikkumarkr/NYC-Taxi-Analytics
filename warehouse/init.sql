-- Create basic schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS quality;

-- Create user for dbt (optional, using admin for now)
-- CREATE USER dbt_user WITH PASSWORD 'dbt_password';
-- GRANT ALL PRIVILEGES ON DATABASE analytics TO dbt_user;
-- GRANT ALL ON SCHEMA raw TO dbt_user;
