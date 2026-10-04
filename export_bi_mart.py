import duckdb
from pathlib import Path
from src.config import WAREHOUSE_PATH, DATA_DIR

def export_for_bi():
    export_dir = DATA_DIR / "processed" / "bi_exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    csv_output = export_dir / "daily_store_performance.csv"
    parquet_output = export_dir / "daily_store_performance.parquet"

    con = duckdb.connect(WAREHOUSE_PATH)

    print("=" * 60)
    print("      EXPORTING ANALYTICAL MARTS FOR BI")
    print("=" * 60)

    # 1. Export CSV for Excel / Power BI
    con.execute(f"""
        COPY daily_store_performance 
        TO '{csv_output.as_posix()}' (HEADER, DELIMITER ',');
    """)
    print(f"Exported CSV:     {csv_output}")

    # 2. Export Parquet for high-speed columnar BI queries
    con.execute(f"""
        COPY daily_store_performance 
        TO '{parquet_output.as_posix()}' (FORMAT PARQUET);
    """)
    print(f"Exported Parquet: {parquet_output}")

    con.close()
    print("\nFiles generated successfully in data/processed/bi_exports/")

if __name__ == "__main__":
    export_for_bi()