import logging
import sys
from src.config import RAW_DATA_PATH, REJECTED_DATA_PATH, WAREHOUSE_PATH
from src.extract import extract_csv_data
from src.validate import validate_and_split
from src.transform import transform_sales_data
from src.load import load_data_to_warehouse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ETL_Pipeline")

def run():
    logger.info("Starting Smart Retail ETL Execution...")

    # 1. EXTRACT
    raw_df = extract_csv_data(RAW_DATA_PATH)

    # 2. VALIDATE & SPLIT
    valid_df, rejected_df = validate_and_split(raw_df)

    if not rejected_df.empty:
        REJECTED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        rejected_df.to_csv(REJECTED_DATA_PATH, index=False)
        logger.info(f"Audit dump saved to {REJECTED_DATA_PATH}")

    # 3. TRANSFORM
    clean_df = transform_sales_data(valid_df)

    # 4. LOAD
    load_data_to_warehouse(clean_df, rejected_df, WAREHOUSE_PATH)

    logger.info("Pipeline executed end-to-end without errors.")

if __name__ == "__main__":
    run()