from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from src.features import add_features, daily_summary

def main():
    raw = ROOT / "data" / "raw" / "btc_usd_candles.csv"
    if not raw.exists():
        raise SystemExit("Raw data not found. Run: python scripts/fetch_data.py")
    df = add_features(pd.read_csv(raw, parse_dates=["timestamp"]))
    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    csv_path = processed / "btc_features.csv"
    parquet_path = processed / "btc_features.parquet"
    df.to_csv(csv_path, index=False)
    try:
        df.to_parquet(parquet_path, index=False)
        print(f"Saved Parquet: {parquet_path}")
    except Exception as exc:
        print(f"Parquet export skipped ({exc}); CSV was saved.")
    daily_summary(df).to_csv(processed / "daily_summary.csv", index=False)
    print(f"Saved {len(df):,} feature rows to {csv_path}")

if __name__ == "__main__":
    main()
