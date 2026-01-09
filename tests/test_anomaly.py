import unittest
import pandas as pd
import numpy as np
from alerts.anomaly_detection import AnomalyDetector

class TestAnomalyDetector(unittest.TestCase):
    def setUp(self):
        # Create a clean signal with one spike
        dates = pd.date_range(start='2024-01-01', periods=30)
        values = [100.0] * 29 + [1000.0] # Massive spike on last day
        self.df_spike = pd.DataFrame({'ds': dates, 'y': values})
        
        # Create a stable signal
        values_stable = [100.0] * 30
        self.df_stable = pd.DataFrame({'ds': dates, 'y': values_stable})

    def test_zscore_spike(self):
        detector = AnomalyDetector(self.df_spike)
        result = detector.check_zscore(threshold=3)
        self.assertIsNotNone(result)
        self.assertEqual(result['method'], 'z_score')
        self.assertEqual(result['actual'], 1000.0)
        self.assertGreater(result['score'], 3)
        print("\n✅ Z-Score Spike Test Passed")

    def test_zscore_stable(self):
        detector = AnomalyDetector(self.df_stable)
        result = detector.check_zscore(threshold=3)
        self.assertIsNone(result)
        print("✅ Z-Score Stable Test Passed")

    def test_dow_baseline(self):
        # Create 5 weeks of data. Mondays are 100, except last Monday is 50.
        dates = pd.date_range(start='2024-01-01', periods=35) # 5 weeks
        values = []
        for d in dates:
            if d.dayofweek == 0: # Monday
                values.append(100.0)
            else:
                values.append(10.0)
                
        # Spike the last Monday (index 28) -> wait, periods=35 means last index 34.
        # 2024-01-01 is Monday.
        # Last day is Feb 4 (Sunday).
        # Let's explicitly set the values.
        df = pd.DataFrame({'ds': dates, 'y': [0]*35})
        
        # Set all Mondays to 100
        mask_mon = df['ds'].dt.dayofweek == 0
        df.loc[mask_mon, 'y'] = 100.0
        
        # Set last Monday (Jan 29) to 50
        last_mon_idx = df[mask_mon].index[-1] 
        df.loc[last_mon_idx, 'y'] = 50.0 
        
        # We need to trim df so the last day IS the anomaly day for the detector to catch it
        # Detector looks at .iloc[-1]
        df_test = df.iloc[:last_mon_idx+1]
        
        detector = AnomalyDetector(df_test)
        result = detector.check_dow_baseline(lookback_weeks=4, threshold_pct=0.2)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['method'], 'dow_baseline')
        self.assertEqual(result['actual'], 50.0)
        self.assertEqual(result['expected'], 100.0)
        self.assertAlmostEqual(result['deviation_pct'], -0.5)
        print("✅ DoW Baseline Test Passed")

if __name__ == '__main__':
    unittest.main()
