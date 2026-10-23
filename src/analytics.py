"""Reusable analytics helpers."""
import pandas as pd

def describe_market(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"rows": 0, "latest_close": None, "mean_return_pct": None,
                "return_std_pct": None, "max_volume": None, "anomaly_count": 0}
    returns = df["return_pct"].dropna() if "return_pct" in df else pd.Series(dtype=float)
    return {
        "rows": int(len(df)),
        "latest_close": float(df["close"].iloc[-1]),
        "mean_return_pct": float(returns.mean()) if not returns.empty else None,
        "return_std_pct": float(returns.std()) if len(returns) > 1 else None,
        "max_volume": float(df["volume"].max()),
        "anomaly_count": int(df["volume_anomaly"].fillna(False).sum()) if "volume_anomaly" in df else 0,
    }
