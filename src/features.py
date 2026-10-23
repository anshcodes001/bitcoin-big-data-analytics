"""Feature engineering for BTC-USD OHLCV candles."""
from __future__ import annotations
import numpy as np
import pandas as pd

REQUIRED = {"timestamp", "open", "high", "low", "close", "volume"}

def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df = frame.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = (df.dropna(subset=list(REQUIRED))
            .drop_duplicates("timestamp")
            .sort_values("timestamp")
            .reset_index(drop=True))
    df = df[(df["close"] > 0) & (df["low"] > 0) & (df["high"] > 0)]
    df["return_pct"] = df["close"].pct_change() * 100
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df["sma_20"] = df["close"].rolling(20, min_periods=1).mean()
    df["sma_50"] = df["close"].rolling(50, min_periods=1).mean()
    df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14, min_periods=14).mean()
    avg_loss = loss.rolling(14, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi_14"] = 100 - (100 / (1 + rs))
    # If the average loss is zero, RSI is 100 for positive momentum.
    df.loc[(avg_loss == 0) & (avg_gain > 0), "rsi_14"] = 100
    prev_close = df["close"].shift(1)
    true_range = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs()
    ], axis=1).max(axis=1)
    df["atr_14"] = true_range.rolling(14, min_periods=1).mean()
    df["volatility_20"] = df["log_return"].rolling(20, min_periods=5).std() * np.sqrt(20)
    volume_mean = df["volume"].rolling(30, min_periods=5).mean()
    volume_std = df["volume"].rolling(30, min_periods=5).std()
    df["volume_zscore"] = (df["volume"] - volume_mean) / volume_std.replace(0, np.nan)
    df["volume_anomaly"] = df["volume_zscore"].abs() >= 3
    df["utc_date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    return df

def daily_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["utc_date", "open", "high", "low", "close", "volume", "return_pct"])
    df = frame.copy()
    df["utc_date"] = pd.to_datetime(df["timestamp"], utc=True).dt.strftime("%Y-%m-%d")
    summary = df.groupby("utc_date", as_index=False).agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    )
    summary["return_pct"] = summary["close"].pct_change() * 100
    return summary
