import logging
from typing import Tuple
import pandas as pd
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

class RetailTransactionSchema(BaseModel):
    transaction_id: str
    store_id: str
    customer_id: str
    product_id: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0.0)
    discount: float = Field(ge=0.0)
    timestamp: str

def validate_and_split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    valid_rows = []
    rejected_rows = []

    logger.info("Executing data quality checks...")

    for _, row in df.iterrows():
        record = row.to_dict()
        try:
            if pd.isna(record.get("transaction_id")) or pd.isna(record.get("timestamp")):
                raise ValueError("Missing primary key or timestamp")

            RetailTransactionSchema(**record)

            gross = record["quantity"] * record["unit_price"]
            if record["discount"] > gross:
                raise ValueError("Discount cannot exceed total line amount")

            valid_rows.append(record)
        except (ValidationError, ValueError) as err:
            record["rejection_reason"] = str(err).split("\n")[0]
            rejected_rows.append(record)

    valid_df = pd.DataFrame(valid_rows)
    rejected_df = pd.DataFrame(rejected_rows)

    logger.info(f"Validation finished: {len(valid_df)} valid, {len(rejected_df)} rejected.")
    return valid_df, rejected_df