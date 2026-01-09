import yaml
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import os
import sys
from anomaly_detection import AnomalyDetector
from root_cause import RootCauseAnalyzer

# Local or Env Config
DB_URL = "postgresql://admin:adminparams@localhost:5432/analytics"

def load_config():
    with open("alerts/alert_rules.yml", "r") as f:
        return yaml.safe_load(f)

def run_alerts():
    config = load_config()
    engine = create_engine(DB_URL)
    
    print("🚀 Starting Anomaly Detection...")
    
    alerts_to_insert = []
    
    with engine.connect() as conn:
        for rule in config['rules']:
            metric = rule['metric']
            print(f"Analysing {metric}...")
            
            # 1. Fetch Data (Last 60 days)
            # Assuming daily grain for now as per rules
            query = f"""
                SELECT pickup_date as ds, {metric} as y
                FROM dbt_dev_marts.mart_kpis_daily
                ORDER BY pickup_date DESC
                LIMIT 60
            """
            
            try:
                df = pd.read_sql(query, conn)
                if len(df) < 5:
                    print(f"⚠️ Not enough data for {metric}")
                    continue
                    
                detector = AnomalyDetector(df)
                
                # Check Methods
                for method_conf in rule['methods']:
                    result = None
                    if method_conf['name'] == 'z_score':
                        result = detector.check_zscore(threshold=method_conf['threshold'])
                    elif method_conf['name'] == 'dow_baseline':
                        result = detector.check_dow_baseline(threshold_pct=method_conf.get('threshold_pct', 0.2))
                        
                    if result:
                        print(f"🚨 ALERT FOUND: {metric} - {result['explanation']}")
                        alerts_to_insert.append({
                            "alert_date": result['date'],
                            "metric_name": metric,
                            "grain": rule['grain'],
                            "metric_value": result['actual'],
                            "expected_value": result['expected'],
                            "deviation_pct": result['deviation_pct'],
                            "severity": result['severity'],
                            "method": result['method'],
                            "explanation": result['explanation']
                        })
                        
            except Exception as e:
                print(f"❌ Error processing {metric}: {e}")

    # Write Alerts
    if alerts_to_insert:
        print(f"Writing {len(alerts_to_insert)} alerts to Postgres...")
        alert_df = pd.DataFrame(alerts_to_insert)
        
        # We need alert_ids to store drivers. 
        # Since we use gen_random_uuid in DB, we should generate them here OR fetch them back.
        # Easier: generate here using python uuid.
        import uuid
        alert_df['alert_id'] = [str(uuid.uuid4()) for _ in range(len(alert_df))]
        
        alert_df.to_sql("kpi_alerts", engine, if_exists="append", index=False)
        print("✅ Alerts Saved.")
        
        # Run Root Cause
        print("🕵️ running Root Cause Analysis...")
        rca = RootCauseAnalyzer(engine)
        all_drivers = []
        
        for record in alerts_to_insert:
            # Find the assigned ID
            matching_row = alert_df[
                (alert_df['metric_name'] == record['metric_name']) & 
                (alert_df['alert_date'] == record['alert_date'])
            ].iloc[0]
            
            record['alert_id'] = matching_row['alert_id']
            record['metric_value'] = matching_row['metric_value'] # Ensure consistency
            
            drivers = rca.analyze(record)
            all_drivers.extend(drivers)
            
        if all_drivers:
            print(f"Writing {len(all_drivers)} drivers...")
            driver_df = pd.DataFrame(all_drivers)
            driver_df.to_sql("kpi_alert_drivers", engine, if_exists="append", index=False)
            print("✅ Drivers Saved.")
            
    else:
        print("✅ No anomalies detected.")

if __name__ == "__main__":
    run_alerts()
