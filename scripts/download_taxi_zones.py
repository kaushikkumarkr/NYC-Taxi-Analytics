import requests
import os
from pathlib import Path

URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv"

def main():
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "taxi_zone_lookup.csv"
    
    if output_path.exists():
        print("⏩ taxi_zone_lookup.csv already exists.")
        return

    print("Downloading taxi_zone_lookup.csv...")
    try:
        r = requests.get(URL)
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(r.content)
        print("✅ Downloaded taxi_zone_lookup.csv")
    except Exception as e:
        print(f"❌ Failed to download zone lookup: {e}")
        exit(1)

if __name__ == "__main__":
    main()
