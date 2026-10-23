"""Local PySpark batch aggregation. For larger data, change master to a Spark cluster."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql import functions as F
    except ImportError as exc:
        raise SystemExit("PySpark missing. Install dependencies with: pip install -r requirements.txt") from exc

    input_path = ROOT / "data" / "processed" / "btc_features.parquet"
    if not input_path.exists():
        raise SystemExit("Features Parquet not found. Run scripts/fetch_data.py then scripts/build_features.py.")
    output_path = ROOT / "data" / "processed" / "spark_daily_summary"
    spark = (SparkSession.builder
             .appName("BitcoinBigDataAnalytics")
             .master("local[*]")
             .getOrCreate())
    spark.sparkContext.setLogLevel("WARN")
    try:
        df = spark.read.parquet(str(input_path))
        df = df.withColumn("timestamp", F.to_timestamp("timestamp"))
        summary = (df.groupBy(F.to_date("timestamp").alias("utc_date"))
                   .agg(
                       F.first("open", ignorenulls=True).alias("first_open"),
                       F.max("high").alias("daily_high"),
                       F.min("low").alias("daily_low"),
                       F.last("close", ignorenulls=True).alias("last_close"),
                       F.sum("volume").alias("total_volume"),
                       F.avg("return_pct").alias("mean_return_pct"),
                       F.max(F.col("volume_anomaly").cast("int")).alias("has_volume_anomaly"),
                       F.count("*").alias("candle_count"),
                   ).orderBy("utc_date"))
        summary.write.mode("overwrite").parquet(str(output_path))
        summary.show(20, truncate=False)
        print(f"Spark output written to: {output_path}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
