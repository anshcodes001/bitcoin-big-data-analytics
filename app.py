from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import pandas as pd
import plotly.express as px
import streamlit as st
from src.features import add_features, daily_summary
from src.analytics import describe_market
from src.market_data import fetch_ticker, fetch_candles

st.set_page_config(page_title="Bitcoin Big Data Analytics", page_icon="₿", layout="wide")
st.title("₿ Bitcoin Market Big Data Analytics")
st.caption("BTC-USD · Coinbase public market data · Educational analytics only")

raw_path = ROOT / "data" / "raw" / "btc_usd_candles.csv"
feature_path = ROOT / "data" / "processed" / "btc_features.csv"

with st.sidebar:
    st.header("Data controls")
    granularity = st.selectbox("Candle interval", [60, 300, 900, 3600, 21600, 86400],
        index=1, format_func=lambda x: {60:"1 minute",300:"5 minutes",900:"15 minutes",3600:"1 hour",21600:"6 hours",86400:"1 day"}[x])
    candle_count = st.slider("Candles to fetch", min_value=100, max_value=3000, value=1000, step=100)
    if st.button("Fetch latest data", type="primary", use_container_width=True):
        try:
            with st.spinner("Fetching public Coinbase candles..."):
                new_df = fetch_candles(granularity=granularity, candles=candle_count)
                if new_df.empty:
                    st.error("No market data returned. Try again later.")
                else:
                    raw_path.parent.mkdir(parents=True, exist_ok=True)
                    new_df.to_csv(raw_path, index=False)
                    feats = add_features(new_df)
                    feature_path.parent.mkdir(parents=True, exist_ok=True)
                    feats.to_csv(feature_path, index=False)
                    try:
                        feats.to_parquet(ROOT / "data" / "processed" / "btc_features.parquet", index=False)
                    except Exception:
                        pass
                    st.success(f"Saved {len(new_df):,} candles.")
                    st.rerun()
        except Exception as exc:
            st.error(f"Fetch failed: {exc}")

if feature_path.exists():
    try:
        df = pd.read_csv(feature_path, parse_dates=["timestamp"])
        df = add_features(df)
    except Exception:
        df = pd.DataFrame()
elif raw_path.exists():
    df = add_features(pd.read_csv(raw_path, parse_dates=["timestamp"]))
else:
    df = pd.DataFrame()

if df.empty:
    st.info("No local data found yet. Use **Fetch latest data** in the sidebar, or run the ingestion scripts in the README.")
    st.code("python scripts/fetch_data.py --granularity 300 --candles 1000\npython scripts/build_features.py\nstreamlit run app.py")
    st.stop()

latest = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest candle close", f"${latest['close']:,.2f}",
            f"{latest['return_pct']:.2f}%" if pd.notna(latest["return_pct"]) else None)
col2.metric("Candles processed", f"{len(df):,}")
col3.metric("Latest RSI (14)", f"{latest['rsi_14']:.1f}" if pd.notna(latest["rsi_14"]) else "N/A")
col4.metric("Volume anomalies", f"{int(df['volume_anomaly'].fillna(False).sum()):,}")

tab1, tab2, tab3, tab4 = st.tabs(["Market overview", "Indicators", "Daily analytics", "Data quality"])
with tab1:
    st.subheader("BTC-USD close price")
    st.plotly_chart(px.line(df, x="timestamp", y="close", title="Close price (USD)"), use_container_width=True)
    st.subheader("Traded volume")
    st.plotly_chart(px.bar(df.tail(250), x="timestamp", y="volume", title="Recent candle volume"), use_container_width=True)
with tab2:
    st.subheader("Moving averages")
    st.plotly_chart(px.line(df, x="timestamp", y=["close", "sma_20", "sma_50", "ema_20"]), use_container_width=True)
    st.subheader("RSI (14)")
    rsi = px.line(df, x="timestamp", y="rsi_14", title="Relative Strength Index")
    rsi.add_hline(y=70, line_dash="dash")
    rsi.add_hline(y=30, line_dash="dash")
    st.plotly_chart(rsi, use_container_width=True)
    st.subheader("Rolling volatility")
    st.plotly_chart(px.line(df, x="timestamp", y="volatility_20"), use_container_width=True)
with tab3:
    daily = daily_summary(df)
    st.plotly_chart(px.bar(daily, x="utc_date", y="volume", title="Daily volume"), use_container_width=True)
    st.dataframe(daily.tail(100), use_container_width=True)
with tab4:
    stats = describe_market(df)
    st.json(stats)
    st.write("Rows with missing values by column")
    st.dataframe(df.isna().sum().rename("missing_count").to_frame(), use_container_width=True)
    st.write("Latest processed records")
    st.dataframe(df.tail(30), use_container_width=True)

st.caption("Data is provided by Coinbase public market-data endpoints. Values can be delayed, incomplete, or subject to API limits. This dashboard does not provide financial advice.")
