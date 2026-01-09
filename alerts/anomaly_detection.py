import pandas as pd
import numpy as np
from scipy import stats

class AnomalyDetector:
    def __init__(self, df):
        """
        df: DataFrame with 'ds' (date/datetime) and 'y' (value) columns.
        sorted by ds asc.
        """
        self.df = df.sort_values('ds').reset_index(drop=True)

    def check_zscore(self, threshold=3.0):
        """
        Detects anomalies using Robust Z-Score (Median/MAD) to avoid outlier skew.
        Returns list of anomalies for the LATEST day only (or window).
        """
        if len(self.df) < 5:
            return None

        # Robust standardization: (x - median) / (mad * 1.4826)
        median = self.df['y'].median()
        mad = stats.median_abs_deviation(self.df['y'], scale='normal') # scale='normal' handles 1.4826 factor
        
        latest = self.df.iloc[-1]
        
        if mad == 0:
            if latest['y'] != median:
                 return {
                    "date": latest['ds'],
                    "method": "z_score",
                    "actual": latest['y'],
                    "expected": median,
                    "deviation_pct": (latest['y'] - median) / median if median != 0 else 0,
                    "score": float('inf'),
                    "severity": "critical",
                    "explanation": f"Value {latest['y']:.2f} differs from constant baseline {median:.2f}"
                }
            return None

        z_score = (latest['y'] - median) / mad
        
        if abs(z_score) > threshold:
            return {
                "date": latest['ds'],
                "method": "z_score",
                "actual": latest['y'],
                "expected": median,
                "deviation_pct": (latest['y'] - median) / median if median != 0 else 0,
                "score": z_score,
                "severity": "critical" if abs(z_score) > threshold * 1.5 else "warning",
                "explanation": f"Value {latest['y']:.2f} is {z_score:.2f} sigma from median {median:.2f}"
            }
        return None

    def check_dow_baseline(self, lookback_weeks=4, threshold_pct=0.2):
        """
        Compares latest value to the average of the same day-of-week over last N weeks.
        """
        latest = self.df.iloc[-1]
        latest_dow = pd.to_datetime(latest['ds']).dayofweek
        
        # Filter for same Day of Week
        history = self.df.iloc[:-1].copy()
        history['dow'] = pd.to_datetime(history['ds']).dt.dayofweek
        same_dow = history[history['dow'] == latest_dow].tail(lookback_weeks)
        
        if len(same_dow) < 2:
            return None

        baseline = same_dow['y'].mean()
        
        if baseline == 0:
            return None
            
        diff_pct = (latest['y'] - baseline) / baseline
        
        if abs(diff_pct) > threshold_pct:
            return {
                "date": latest['ds'],
                "method": "dow_baseline",
                "actual": latest['y'],
                "expected": baseline,
                "deviation_pct": diff_pct,
                "score": diff_pct,
                "severity": "critical" if abs(diff_pct) > threshold_pct * 2 else "warning",
                "explanation": f"Value {latest['y']:.2f} is {diff_pct:.0%} from {lookback_weeks}-week avg {baseline:.2f}"
            }
        return None
