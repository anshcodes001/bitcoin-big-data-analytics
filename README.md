# Bitcoin Market Big Data Analytics

A BTC-USD-only market-data analytics project built with Python, Pandas, PySpark, and Streamlit. It ingests public Coinbase Exchange candle data, engineers time-series features, and presents exploratory market analytics in a dashboard.

> **Disclaimer:** Educational project only. It is not financial advice, a trading bot, or a guarantee of future price movements.

## Highlights

- Fetch historical BTC-USD OHLCV candles from Coinbase's public Exchange API.
- Clean, deduplicate, and sort time-series data.
- Calculate returns, SMA, EMA, RSI, ATR, rolling volatility, and volume anomaly indicators.
- Export processed data to CSV and Parquet.
- Run daily aggregations with PySpark.
- Explore market data in a Streamlit dashboard.
- Run unit tests for core feature engineering.
- Optional JSONL event simulator for demonstrating event-ingestion concepts.

## Architecture

```text
Coinbase public market-data API
              |
              v
      Historical ingestion
       (scripts/fetch_data.py)
              |
              v
       Raw BTC-USD candles
         data/raw/*.csv
              |
              v
      Feature engineering
      (src/features.py)
              |
        +-----+------+
        |            |
        v            v
   CSV / Parquet   Daily summaries
        |
        +---------------------+
        |                     |
        v                     v
 Streamlit dashboard     PySpark batch job
       app.py          scripts/run_spark_job.py
```

The optional `scripts/stream_simulator.py` writes demonstration events based on the latest stored candle. It is **not** a genuine exchange WebSocket feed or a production streaming pipeline.

## Tech stack

- Python 3.10+
- Pandas and NumPy
- Coinbase Exchange public REST API
- PySpark
- Streamlit and Plotly
- PyArrow / Parquet
- `unittest`

## Requirements

- Python 3.10 or newer
- Java runtime compatible with the installed PySpark version (Java 17 is a good starting point for recent Spark releases)
- Internet access to fetch public market data

## Setup

### Windows (PowerShell)

```powershell
git clone https://github.com/YOUR-USERNAME/bitcoin-big-data-analytics.git
cd bitcoin-big-data-analytics

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
git clone https://github.com/YOUR-USERNAME/bitcoin-big-data-analytics.git
cd bitcoin-big-data-analytics

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Replace `YOUR-USERNAME` with your GitHub username after creating the repository. Alternatively, download the repository ZIP from GitHub.

## Run the project

### 1. Fetch historical BTC-USD candles

```bash
python scripts/fetch_data.py --granularity 300 --candles 1000
```

Granularity is in seconds. Supported intervals: `60`, `300`, `900`, `3600`, `21600`, `86400`.

This saves the fetched candles to `data/raw/btc_usd_candles.csv`. Public API availability and rate limits may vary.

### 2. Build analytics features

```bash
python scripts/build_features.py
```

Creates the feature dataset and daily summary under `data/processed/`.

### 3. Launch the dashboard

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

### 4. Run PySpark batch analytics

First fetch the data and build features. Then run:

```bash
python scripts/run_spark_job.py
```

The job reads Parquet data, groups candles by UTC date, computes daily statistics, and writes output to `data/processed/spark_daily_summary/`.

### 5. Run the optional event simulator

```bash
python scripts/stream_simulator.py --interval 5
```

Press `Ctrl+C` to stop. Events are appended to `data/stream/btc_events.jsonl`. This is a local event-ingestion demo only.

### 6. Run tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
bitcoin-big-data-analytics/
├── .github/
│   └── workflows/
│       └── tests.yml
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── requirements.txt
├── requirements-dev.txt
├── app.py
├── src/
│   ├── __init__.py
│   ├── analytics.py
│   ├── features.py
│   └── market_data.py
├── scripts/
│   ├── build_features.py
│   ├── fetch_data.py
│   ├── run_spark_job.py
│   └── stream_simulator.py
├── tests/
│   └── test_features.py
└── data/
    ├── raw/
    ├── processed/
    └── stream/
```

Generated datasets are excluded from Git so the repository stays small and doesn't accidentally commit large or frequently changing market-data files.

## Feature definitions

| Feature | Description |
|---|---|
| `return_pct` | Percentage change in close price |
| `log_return` | Natural logarithm of current close divided by previous close |
| `sma_20`, `sma_50` | Simple moving averages |
| `ema_20` | Exponential moving average |
| `rsi_14` | 14-period relative strength index |
| `atr_14` | 14-period average true range |
| `volatility_20` | Rolling standard deviation of log returns, scaled by square root of 20 |
| `volume_zscore` | Standardized rolling volume deviation |
| `volume_anomaly` | Flag for absolute volume z-score at least 3 |

Indicators are descriptive calculations and should not be interpreted as trading recommendations.

## Data source and attribution

Market data is fetched from the public Coinbase Exchange API:
- API documentation: https://docs.cdp.coinbase.com/exchange/reference/exchangerestapi_getproductcandles
- Product: `BTC-USD`

Follow the provider's usage terms, API limits, and data policies.

## Known limitations

- Public API responses may be incomplete, rate-limited, or unavailable.
- The starter project uses a local Spark master (`local[*]`); configure a cluster separately for distributed multi-node execution.
- The stream simulator is not a live market stream.
- Forecasting, model training, and trading execution are not implemented.
- Runtime behavior can vary by Python, Java, Spark, and operating-system versions.

## Roadmap

- [ ] Add a true WebSocket market-data consumer.
- [ ] Integrate Kafka for real-time event transport.
- [ ] Add Spark Structured Streaming with checkpointing.
- [ ] Add data-quality checks and integration tests.
- [ ] Add Docker Compose for reproducible local setup.
- [ ] Add optional, rigorously evaluated time-series forecasting.

## License

Released under the MIT License. See [LICENSE](LICENSE).
