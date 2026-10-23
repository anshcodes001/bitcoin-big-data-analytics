"""Optional JSONL event simulator. It re-emits the latest candle; not a live exchange feed."""
import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between demonstration events")
    args = parser.parse_args()
    source = ROOT / "data" / "raw" / "btc_usd_candles.csv"
    target = ROOT / "data" / "stream" / "btc_events.jsonl"
    if not source.exists():
        raise SystemExit("Run scripts/fetch_data.py first.")
    target.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(source)
    latest = df.iloc[-1].to_dict()
    print("Writing demonstration events. Ctrl+C to stop.")
    try:
        while True:
            event = {
                "event_time": datetime.now(timezone.utc).isoformat(),
                "product": "BTC-USD",
                "event_type": "latest_candle_snapshot_demo",
                "candle": latest,
            }
            with target.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, default=str) + "\n")
            print(event["event_time"], "BTC-USD close =", latest.get("close"))
            time.sleep(max(0.5, args.interval))
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
