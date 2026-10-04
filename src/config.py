from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

RAW_DATA_PATH = DATA_DIR / "raw" / "transactions_raw.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "transactions_clean.parquet"
REJECTED_DATA_PATH = DATA_DIR / "rejected" / "rejected_records.csv"

# DuckDB Warehouse path
WAREHOUSE_PATH = str(DATA_DIR / "retail_warehouse.duckdb")