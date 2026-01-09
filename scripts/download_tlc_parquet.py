import argparse
import requests
import os
import sys
from pathlib import Path

# Constants
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
CHUNK_SIZE = 8192

def download_file(url, output_path):
    fn = output_path.name
    print(f"Downloading {fn}...")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
        print(f"✅ Downloaded {fn}")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ File not found: {url}")
        else:
            print(f"❌ Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download NYC TLC Trip Data")
    parser.add_argument("--months", type=str, required=True, help="Comma-separated YYYY-MM (e.g., 2024-01,2024-02)")
    parser.add_argument("--type", type=str, default="yellow", choices=["yellow", "green", "fhv"], help="Trip type")
    parser.add_argument("--output-dir", type=str, default="data/raw", help="Output directory")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    months = [m.strip() for m in args.months.split(",")]
    
    success_count = 0
    for month in months:
        filename = f"{args.type}_tripdata_{month}.parquet"
        url = f"{BASE_URL}/{filename}"
        output_path = output_dir / filename
        
        if output_path.exists():
            print(f"⏩ Skipping {filename}, already exists.")
            success_count += 1
            continue
            
        if download_file(url, output_path):
            success_count += 1
            
    if success_count == len(months):
        print(f"🎉 All {len(months)} files ready.")
        sys.exit(0)
    else:
        print(f"⚠️ Only {success_count}/{len(months)} downloaded.")
        sys.exit(1)

if __name__ == "__main__":
    main()
