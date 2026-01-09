import os
import pandas as pd
import logging
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Configuration
YEAR = 2024
MONTH = 1
# 10% Sample ensures we fit comfortably in 500MB limit (300k rows)
SAMPLE_FRACTION = 0.1 
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

# Database Connection
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "adminparams")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "analytics")
DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_url(year, month):
    return f"{BASE_URL}/yellow_tripdata_{year}-{month:02d}.parquet"

def main():
    engine = create_engine(DATABASE_URI)
    
    logger.info(f"🚀 Starting Production Snapshot Ingestion ({YEAR}-{MONTH:02d})")
    logger.info(f"🎯 Sampling Rate: {SAMPLE_FRACTION*100}% (Optimized for Free Tier)")

    url = get_url(YEAR, MONTH)
    try:
        logger.info(f"   ⬇️ Downloading data from {url}...")
        df = pd.read_parquet(url)
        
        # Sample
        original_len = len(df)
        df_sampled = df.sample(frac=SAMPLE_FRACTION, random_state=42)
        sampled_len = len(df_sampled)
        
        logger.info(f"   ✂️ Reduced rows from {original_len:,} to {sampled_len:,}")
        
        # Clean Columns
        df_sampled.columns = [c.lower() for c in df_sampled.columns]
        
        # Load Strategy: Drop Cascade (Kill Old Schema) -> Replace (New Schema)
        # This handles the migration from MixedCase to lowercase columns
        with engine.begin() as conn:
            logger.info("   🔥 Dropping table 'raw.yellow_trips' (CASCADE) to allow schema update...")
            conn.execute(text("DROP TABLE IF EXISTS raw.yellow_trips CASCADE;"))
        
        logger.info(f"   💾 Loading {len(df_sampled):,} rows to Postgres (Chunked)...")
        # Use replace since we just dropped it, but 'replace' handles creation.
        df_sampled.to_sql('yellow_trips', engine, schema='raw', if_exists='replace', index=False, chunksize=10000) 
        
        logger.info("✅ Snapshot Ingestion Complete. Ready for Production.")
        
    except Exception as e:
        logger.error(f"❌ Failed to process snapshot: {e}")
        exit(1)

if __name__ == "__main__":
    main()
