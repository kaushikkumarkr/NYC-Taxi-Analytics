import argparse
import pandas as pd
from pathlib import Path
import os

def main():
    parser = argparse.ArgumentParser(description="Create a dev sample from a parquet file")
    parser.add_argument("--input", type=str, required=True, help="Input parquet file path")
    parser.add_argument("--output", type=str, default="data/raw/yellow_tripdata_sample.parquet", help="Output sample path")
    parser.add_argument("--rows", type=int, default=100000, help="Number of rows to sample")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Input file {args.input} does not exist.")
        exit(1)
        
    print(f"Reading {args.input}...")
    try:
        # Use pyarrow to read efficiently, but pandas read_parquet is usually fine for 1 month
        df = pd.read_parquet(args.input)
        
        sample_size = min(len(df), args.rows)
        print(f"Sampling {sample_size} rows from {len(df)} total rows...")
        
        df_sample = df.sample(n=sample_size, random_state=42)
        
        df_sample.to_parquet(args.output)
        print(f"✅ Created sample at {args.output}")
        
    except Exception as e:
        print(f"❌ Error creating sample: {e}")
        exit(1)

if __name__ == "__main__":
    main()
