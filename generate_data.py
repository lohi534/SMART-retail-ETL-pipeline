import random
from datetime import datetime, timedelta
import pandas as pd
from src.config import RAW_DATA_PATH

random.seed(42)

STORES = ["STR-101", "STR-102", "STR-103", "STR-104"]
PRODUCTS = [
    {"product_id": "PRD-001", "name": "Organic Milk", "price": 4.50},
    {"product_id": "PRD-002", "name": "Whole Wheat Bread", "price": 2.80},
    {"product_id": "PRD-003", "name": "Arabica Coffee Beans", "price": 14.99},
    {"product_id": "PRD-004", "name": "Greek Yogurt", "price": 1.99},
    {"product_id": "PRD-005", "name": "Extra Virgin Olive Oil", "price": 18.50},
]

def generate_sample_data(num_rows: int = 500):
    rows = []
    base_time = datetime.now() - timedelta(days=5)

    for i in range(1, num_rows + 1):
        product = random.choice(PRODUCTS)
        is_corrupt = random.random() < 0.08  # ~8% faulty data to test quality checks

        if is_corrupt:
            anomaly = random.choice(["missing_id", "negative_qty", "excessive_discount", "missing_timestamp"])
            txn_id = None if anomaly == "missing_id" else f"TXN-{1000 + i}"
            qty = -2 if anomaly == "negative_qty" else random.randint(1, 5)
            discount = 100.0 if anomaly == "excessive_discount" else 0.5
            timestamp = None if anomaly == "missing_timestamp" else (base_time + timedelta(minutes=i * 12)).isoformat()
        else:
            txn_id = f"TXN-{1000 + i}"
            qty = random.randint(1, 8)
            discount = round(random.uniform(0.0, 1.5), 2)
            timestamp = (base_time + timedelta(minutes=i * 12)).isoformat()

        rows.append({
            "transaction_id": txn_id,
            "store_id": random.choice(STORES),
            "customer_id": f"CUST-{random.randint(100, 250)}",
            "product_id": product["product_id"],
            "product_name": product["name"],
            "quantity": qty,
            "unit_price": product["price"],
            "discount": discount,
            "timestamp": timestamp
        })

    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"Generated {len(df)} transactions into {RAW_DATA_PATH}")

if __name__ == "__main__":
    generate_sample_data()