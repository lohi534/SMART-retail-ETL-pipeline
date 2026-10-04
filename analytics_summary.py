import duckdb
from src.config import WAREHOUSE_PATH

def generate_analytics_mart():
    con = duckdb.connect(WAREHOUSE_PATH)

    # Create daily aggregated reporting table
    con.execute("""
        CREATE OR REPLACE TABLE daily_store_performance AS
        SELECT 
            date_key,
            store_id,
            COUNT(DISTINCT transaction_id) AS total_orders,
            COUNT(DISTINCT customer_id) AS unique_customers,
            SUM(quantity) AS units_sold,
            ROUND(SUM(gross_amount), 2) AS gross_sales,
            ROUND(SUM(discount), 2) AS total_discounts,
            ROUND(SUM(net_amount), 2) AS net_revenue,
            ROUND(AVG(net_amount), 2) AS avg_basket_value
        FROM fact_sales
        GROUP BY date_key, store_id
        ORDER BY date_key DESC, net_revenue DESC;
    """)

    print("\n" + "="*60)
    print("      DAILY STORE PERFORMANCE MART (TOP 10 ROWS)")
    print("="*60)
    df = con.execute("SELECT * FROM daily_store_performance LIMIT 10").fetchdf()
    print(df.to_string(index=False))

    con.close()

if __name__ == "__main__":
    generate_analytics_mart()