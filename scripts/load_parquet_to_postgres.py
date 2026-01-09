import argparse
import pandas as pd
import sqlalchemy
from sqlalchemy import text
import os
import io

# Validating environment variable for URL
DATABASE_URL = "postgresql://admin:adminparams@localhost:5432/analytics"

def get_engine():
    return sqlalchemy.create_engine(DATABASE_URL)

def load_zone_lookup(csv_path):
    print(f"Loading {csv_path} to raw.taxi_zone_lookup...")
    engine = get_engine()
    df = pd.read_csv(csv_path)
    
    # Simple replace
    # Use explicit DROP CASCADE to handle dbt view dependencies
    # We use engine.begin() for a transaction that auto-commits
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS raw.taxi_zone_lookup CASCADE;"))
        df.to_sql("taxi_zone_lookup", conn, schema="raw", if_exists="replace", index=False)
        # Add primary key
        conn.execute(text("ALTER TABLE raw.taxi_zone_lookup ADD PRIMARY KEY (\"LocationID\");"))
    print("✅ Loaded taxi_zone_lookup")

def load_parquet(file_path, table_name):
    print(f"Loading {file_path} to raw.{table_name}...")
    engine = get_engine()
    
    # Read parquet
    df = pd.read_parquet(file_path)
    
    # Add metadata
    df['filename'] = os.path.basename(file_path)
    df['load_timestamp'] = pd.Timestamp.now()
    
    # Standardize to lowercase columns to match Postgres schema
    df.columns = [c.lower() for c in df.columns]
    
    # We use 'replace' for the first chunk if we were looping, but for file-based:
    # If table doesn't exist, create it. If it exists, append.
    # For idempotency in this script, we can default to append, but let's provide a flag or just append.
    # Actually, for 'raw', we might want to truncate if we are reloading the same month?
    # For now, let's just Append.
    
    try:
        with engine.connect() as conn:
            # Pandas to_sql is slow for millions of rows. 
            # Optimization: Write to CSV buffer and COPY.
            
            # Create table if not exists (using pandas for schema inference, empty df)
            # This is a bit tricky with COPY. 
            # Fallback: Use fast_executemany approaches or just standard to_sql for "dev mode" speed (100k rows is fast).
            # For Prod (millions), we'd want COPY. Using to_sql with method='multi' or chunksize.
            
            # Let's stick to standard to_sql with chunksize for simplicity and compatibility first.
            
            df.to_sql(table_name, conn, schema="raw", if_exists="append", index=False, chunksize=10000)
            
        print(f"✅ Loaded {len(df)} rows to raw.{table_name}")
    except Exception as e:
        print(f"❌ Failed to load {file_path}: {e}")
        raise e

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, help="Path to parquet file")
    parser.add_argument("--zones", type=str, help="Path to zone lookup csv")
    parser.add_argument("--table", type=str, default="yellow_trips", help="Target table name in raw schema")
    
    args = parser.parse_args()
    
    if args.zones:
        load_zone_lookup(args.zones)
        
    if args.file:
        load_parquet(args.file, args.table)
        
if __name__ == "__main__":
    main()
