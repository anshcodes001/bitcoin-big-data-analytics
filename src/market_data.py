"""Coinbase Exchange public candle data client. No API key is required."""
from __future__ import annotations
import time
from datetime import datetime, timezone
from typing import Iterable
import pandas as pd
import requests

BASE_URL = "https://api.exchange.coinbase.com"
VALID_GRANULARITIES = {60, 300, 900, 3600, 21600, 86400}
COLUMNS = ["time", "low", "high", "open", "close", "volume"]

def fetch_candles(product: str = "BTC-USD", granularity: int = 300,
                  candles: int = 1000, pause: float = 0.25) -> pd.DataFrame:
    """Fetch up to `candles` recent candles in API-sized chunks.

    Coinbase candle requests are limited to a few hundred rows. We query
    backwards in windows, normalize the response, deduplicate timestamps,
    then return ascending time order.
    """
    if product != "BTC-USD":
        raise ValueError("This project is configured for BTC-USD only.")
    if granularity not in VALID_GRANULARITIES:
        raise ValueError(f"Unsupported granularity: {granularity}")
    if candles < 1:
        raise ValueError("candles must be positive")

    session = requests.Session()
    session.headers.update({"User-Agent": "bitcoin-big-data-analytics/1.0"})
    now = int(datetime.now(timezone.utc).timestamp())
    all_rows = []
    remaining = candles
    end_ts = now

    while remaining > 0:
        batch_size = min(300, remaining)
        start_ts = end_ts - (batch_size * granularity)
        url = f"{BASE_URL}/products/{product}/candles"
        response = session.get(
            url,
            params={"granularity": granularity, "start": start_ts, "end": end_ts},
            timeout=20,
        )
        if response.status_code == 429:
            time.sleep(max(pause, 1.5))
            response.raise_for_status()
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise RuntimeError(f"Unexpected Coinbase response: {payload}")
        all_rows.extend(payload)
        remaining -= batch_size
        end_ts = start_ts
        if not payload:
            break
        time.sleep(pause)

    if not all_rows:
        return pd.DataFrame(columns=["timestamp", "low", "high", "open", "close", "volume"])

    # Coinbase Exchange candle order: [time, low, high, open, close, volume]
    df = pd.DataFrame(all_rows, columns=COLUMNS)
    df["timestamp"] = pd.to_datetime(df.pop("time"), unit="s", utc=True)
    for col in ["low", "high", "open", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = (df.dropna()
            .drop_duplicates(subset=["timestamp"])
            .sort_values("timestamp")
            .reset_index(drop=True))
    return df[["timestamp", "open", "high", "low", "close", "volume"]]

def fetch_ticker(product: str = "BTC-USD") -> dict:
    """Fetch a public ticker snapshot."""
    if product != "BTC-USD":
        raise ValueError("This project is configured for BTC-USD only.")
    response = requests.get(
        f"{BASE_URL}/products/{product}/ticker",
        headers={"User-Agent": "bitcoin-big-data-analytics/1.0"},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "product": product,
        "price": float(data["price"]),
        "size": float(data.get("size", 0)),
        "time": data.get("time"),
        "bid": float(data.get("bid", 0)),
        "ask": float(data.get("ask", 0)),
    }
