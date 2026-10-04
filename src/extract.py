import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

def extract_csv_data(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found at: {file_path}")

    logger.info(f"Extracting data from {file_path}")
    df = pd.read_csv(file_path, dtype={"transaction_id": str, "store_id": str, "product_id": str})
    logger.info(f"Extracted {len(df)} rows from raw source.")
    return df