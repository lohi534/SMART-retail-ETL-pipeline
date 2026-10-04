import pytest
import pandas as pd
from src.validate import validate_and_split
from src.transform import transform_sales_data

def test_validation_splits_clean_and_corrupt_records():
    # 1. Provide fake rows with deliberate errors
    raw_sample = pd.DataFrame([
        {
            # Valid record
            "transaction_id": "TXN-901",
            "store_id": "STR-101",
            "customer_id": "CUST-01",
            "product_id": "PRD-001",
            "quantity": 2,
            "unit_price": 10.0,
            "discount": 1.0,
            "timestamp": "2026-10-04T12:00:00"
        },
        {
            # Invalid: Negative quantity (-2)
            "transaction_id": "TXN-902",
            "store_id": "STR-101",
            "customer_id": "CUST-02",
            "product_id": "PRD-001",
            "quantity": -2,
            "unit_price": 10.0,
            "discount": 0.0,
            "timestamp": "2026-10-04T12:05:00"
        },
        {
            # Invalid: Missing transaction ID (None)
            "transaction_id": None,
            "store_id": "STR-102",
            "customer_id": "CUST-03",
            "product_id": "PRD-002",
            "quantity": 1,
            "unit_price": 5.0,
            "discount": 0.0,
            "timestamp": "2026-10-04T12:10:00"
        }
    ])

    # 2. Run your pipeline's validation logic
    valid_df, rejected_df = validate_and_split(raw_sample)

    # 3. Assert the validator correctly separated good vs bad data
    assert len(valid_df) == 1, "Expected exactly 1 valid record"
    assert len(rejected_df) == 2, "Expected exactly 2 rejected records"
    assert valid_df.iloc[0]["transaction_id"] == "TXN-901"

def test_transformation_computes_financial_metrics():
    # 1. Provide a single clean record
    clean_sample = pd.DataFrame([
        {
            "transaction_id": "TXN-901",
            "store_id": "STR-101",
            "customer_id": "CUST-01",
            "product_id": "PRD-001",
            "quantity": 3,
            "unit_price": 20.0,
            "discount": 5.0,
            "timestamp": "2026-10-04T14:30:00"
        }
    ])

    # 2. Run the transformation logic
    transformed = transform_sales_data(clean_sample)

    # 3. Assert calculations are mathematically accurate
    # Gross: 3 * 20.0 = 60.00
    # Net: 60.00 - 5.0 = 55.00
    assert transformed.iloc[0]["gross_amount"] == 60.00
    assert transformed.iloc[0]["net_amount"] == 55.00
    assert transformed.iloc[0]["date_key"] == 20261004
    assert transformed.iloc[0]["hour"] == 14