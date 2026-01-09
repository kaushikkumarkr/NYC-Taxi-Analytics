import sys
import psycopg2
import requests
import time

def check_postgres():
    print("Checking Postgres connection...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="analytics",
            user="admin",
            password="adminparams"
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        print("✅ Postgres connection successful")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Postgres connection failed: {e}")
        return False

def check_url(name, url):
    print(f"Checking {name} at {url}...")
    try:
        response = requests.get(url)
        if response.status_code < 400:
            print(f"✅ {name} is up (Status: {response.status_code})")
            return True
        else:
            print(f"⚠️ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} check failed: {e}")
        return False

if __name__ == "__main__":
    pg = check_postgres()
    dagster = check_url("Dagster", "http://localhost:3000")
    superset = check_url("Superset", "http://localhost:8088/health")
    
    if pg and dagster and superset:
        print("\n🎉 All systems operational!")
        sys.exit(0)
    else:
        print("\n❌ System check failed.")
        sys.exit(1)
