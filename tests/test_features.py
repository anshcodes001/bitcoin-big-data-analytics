import sys
from pathlib import Path
import unittest
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.features import add_features, daily_summary

class FeatureTests(unittest.TestCase):
    def sample(self):
        times = pd.date_range("2025-01-01", periods=40, freq="5min", tz="UTC")
        close = [100 + i for i in range(40)]
        return pd.DataFrame({
            "timestamp": times,
            "open": close,
            "high": [x + 2 for x in close],
            "low": [x - 2 for x in close],
            "close": close,
            "volume": [10 + i for i in range(40)],
        })

    def test_features_added(self):
        result = add_features(self.sample())
        for col in ["return_pct", "sma_20", "ema_20", "rsi_14", "atr_14", "volume_anomaly"]:
            self.assertIn(col, result.columns)
        self.assertEqual(len(result), 40)

    def test_sorted_and_deduplicated(self):
        df = self.sample().iloc[::-1]
        df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        result = add_features(df)
        self.assertTrue(result["timestamp"].is_monotonic_increasing)
        self.assertEqual(result["timestamp"].nunique(), len(result))

    def test_daily_summary(self):
        result = daily_summary(add_features(self.sample()))
        self.assertGreaterEqual(len(result), 1)
        self.assertIn("volume", result.columns)
        self.assertIn("return_pct", result.columns)

if __name__ == "__main__":
    unittest.main()
