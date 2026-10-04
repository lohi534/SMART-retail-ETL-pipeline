import logging
import duckdb
import pandas as pd

logger = logging.getLogger(__name__)

def load_data_to_warehouse(valid_df: pd.DataFrame, rejected_df: pd.DataFrame, db_path: str):
    logger.info(f"Writing to warehouse: {db_path}")
    con = duckdb.connect(db_path)

    # Initialize Star Schema tables
    con.execute("""
        CREATE TABLE IF NOT EXISTS fact_sales (
            transaction_id VARCHAR,
            store_id VARCHAR,
            customer_id VARCHAR,
            product_id VARCHAR,
            date_key INTEGER,
            quantity INTEGER,
            unit_price DOUBLE,
            discount DOUBLE,
            gross_amount DOUBLE,
            net_amount DOUBLE,
            timestamp TIMESTAMP,
            etl_processed_at TIMESTAMP,
            PRIMARY KEY (transaction_id, product_id)
        );

        CREATE TABLE IF NOT EXISTS rejected_sales_audit (
            transaction_id VARCHAR,
            store_id VARCHAR,
            product_id VARCHAR,
            rejection_reason VARCHAR,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    if not valid_df.empty:
        con.register("df_valid_stage", valid_df)
        con.execute("""
            INSERT OR REPLACE INTO fact_sales
            SELECT 
                transaction_id, store_id, customer_id, product_id,
                date_key, quantity, unit_price, discount,
                gross_amount, net_amount, timestamp, etl_processed_at
            FROM df_valid_stage
        """)

    if not rejected_df.empty:
        con.register("df_rejected_stage", rejected_df)
        con.execute("""
            INSERT INTO rejected_sales_audit (transaction_id, store_id, product_id, rejection_reason)
            SELECT transaction_id, store_id, product_id, rejection_reason
            FROM df_rejected_stage
        """)

    con.close()
    logger.info("Warehouse tables populated successfully.")