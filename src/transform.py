import logging
from datetime import datetime, timezone
import pandas as pd

logger = logging.getLogger(__name__)

def transform_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    logger.info("Enriching transactions and generating derived metrics...")
    transformed = df.copy()

    transformed["timestamp"] = pd.to_datetime(transformed["timestamp"])
    transformed["date_key"] = transformed["timestamp"].dt.strftime("%Y%m%d").astype(int)
    transformed["hour"] = transformed["timestamp"].dt.hour
    transformed["day_of_week"] = transformed["timestamp"].dt.day_name()

    transformed["gross_amount"] = (transformed["quantity"] * transformed["unit_price"]).round(2)
    transformed["net_amount"] = (transformed["gross_amount"] - transformed["discount"]).round(2)
    transformed["etl_processed_at"] = datetime.now(timezone.utc)

    # Deduplicate idempotent runs
    transformed = transformed.drop_duplicates(subset=["transaction_id", "product_id"], keep="last")
    return transformed