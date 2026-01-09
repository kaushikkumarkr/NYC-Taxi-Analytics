import pandas as pd
from sqlalchemy import text

class RootCauseAnalyzer:
    def __init__(self, engine):
        self.engine = engine
        
    def analyze(self, alert):
        """
        alert: dict with keys [alert_id, metric_name, alert_date, grain]
        """
        drivers = []
        
        # Only support Daily for now
        if alert['grain'] != 'daily':
            return []
            
        print(f"🔎 Investigating drivers for {alert['metric_name']} on {alert['alert_date']}...")
        
        # 1. Zone Breakdown
        zone_drivers = self._analyze_dimension(
            alert, 
            dimension_table="dbt_dev_marts.mart_kpis_by_zone_daily",
            join_dim="dbt_dev_marts.dim_taxi_zone",
            join_key="location_id",
            fact_key="pickup_location_id",
            dim_name_col="zone",
            metric_col="total_trips" if "trips" in alert['metric_name'] else "total_revenue" 
        )
        drivers.extend(zone_drivers)

        # 2. Payment Breakdown
        payment_drivers = self._analyze_dimension(
            alert,
            dimension_table="dbt_dev_marts.mart_kpis_by_payment_daily",
            join_dim=None,
            join_key=None,
            fact_key="payment_type",
            dim_name_col="payment_type",
            metric_col="total_trips" if "trips" in alert['metric_name'] else "total_revenue"
        )
        drivers.extend(payment_drivers)
        
        return drivers

    def _analyze_dimension(self, alert, dimension_table, join_dim, join_key, fact_key, dim_name_col, metric_col):
        # Compare Alert Date vs Avg of Prev 4 same-weekdays
        # Simple query to get delta per segment
        
        date_str = str(alert['alert_date'])
        
        query = f"""
        WITH baseline AS (
            SELECT 
                {fact_key} as segment_id,
                avg({metric_col}) as baseline_val
            FROM {dimension_table}
            WHERE pickup_date < '{date_str}'::date 
              AND pickup_date >= '{date_str}'::date - INTERVAL '28 days'
              AND extract(dow from pickup_date) = extract(dow from '{date_str}'::date)
            GROUP BY 1
        ),
        current_day AS (
            SELECT 
                {fact_key} as segment_id,
                {metric_col} as current_val
            FROM {dimension_table}
            WHERE pickup_date = '{date_str}'::date
        )
        SELECT 
            coalesce(b.segment_id, c.segment_id) as segment_id,
            cast(coalesce(PLACEHOLDER_SEGMENT_NAME, cast(coalesce(b.segment_id, c.segment_id) as varchar)) as varchar) as segment_name,
            coalesce(b.baseline_val, 0) as baseline,
            coalesce(c.current_val, 0) as current,
            coalesce(c.current_val, 0) - coalesce(b.baseline_val, 0) as delta
        FROM baseline b
        FULL OUTER JOIN current_day c ON b.segment_id = c.segment_id
        """
        
        if join_dim:
             segment_name_expresssion = f"d.{dim_name_col}"
             query += f" LEFT JOIN {join_dim} d ON coalesce(b.segment_id, c.segment_id) = d.{join_key}"
        else:
             segment_name_expresssion = "cast(coalesce(b.segment_id, c.segment_id) as varchar)"
             # Mock join not needed if we don't select from d, but let's keep it simple
             
        query = query.replace("PLACEHOLDER_SEGMENT_NAME", segment_name_expresssion)

        query += " ORDER BY abs(coalesce(c.current_val, 0) - coalesce(b.baseline_val, 0)) DESC LIMIT 3"
        
        try:
            df = pd.read_sql(query, self.engine)
            results = []
            for idx, row in df.iterrows():
                # Avoid noise
                if abs(row['delta']) < 10: 
                    continue
                    
                total_gap = abs(alert.get('metric_value', 0) - alert.get('expected_value', 0))
                contrib = abs(row['delta']) / total_gap if total_gap > 0 else 0
                
                results.append({
                    "alert_id": alert.get('alert_id'), # Might be None if not yet persisted, handled by runner
                    "dimension": dim_name_col,
                    "segment_value": str(row['segment_name']),
                    "baseline_value": float(row['baseline']),
                    "current_value": float(row['current']),
                    "delta": float(row['delta']),
                    "contribution_pct": contrib,
                    "rank": idx + 1
                })
            return results
        except Exception as e:
            print(f"❌ Error analyzing dimension {dimension_table}: {e}")
            return []
