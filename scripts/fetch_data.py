import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.market_data import fetch_candles

def main():
    parser = argparse.ArgumentParser(description="Fetch public BTC-USD candles from Coinbase.")
    parser.add_argument("--granularity", type=int, default=300,
                        help="Candle interval seconds: 60, 300, 900, 3600, 21600, 86400")
    parser.add_argument("--candles", type=int, default=1000, help="Number of candles to request")
    args = parser.parse_args()
    out = ROOT / "data" / "raw" / "btc_usd_candles.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df = fetch_candles(granularity=args.granularity, candles=args.candles)
    if df.empty:
        raise SystemExit("No candles returned. Try again later.")
    df.to_csv(out, index=False)
    print(f"Saved {len(df):,} candles to {out}")
    print(df.tail(3).to_string(index=False))

if __name__ == "__main__":
    main()
