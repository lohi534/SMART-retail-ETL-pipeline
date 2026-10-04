import duckdb
from src.config import WAREHOUSE_PATH

def query_warehouse():
    con = duckdb.connect(WAREHOUSE_PATH)

    print("\n" + "="*50)
    print("        WAREHOUSE SUMMARY METRICS")
    print("="*50)

    # 1. Row counts
    fact_count = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    rejected_count = con.execute("SELECT COUNT(*) FROM rejected_sales_audit").fetchone()[0]
    print(f"Total Fact Sales Loaded:    {fact_count}")
    print(f"Total Rejected Rows Audited: {rejected_count}")

    # 2. Revenue by Store
    print("\n" + "-"*50)
    print("STORE PERFORMANCE SUMMARY (Revenue & Units)")
    print("-"*50)
    store_summary = con.execute("""
        SELECT 
            store_id,
            SUM(quantity) AS total_units_sold,
            ROUND(SUM(gross_amount), 2) AS gross_revenue,
            ROUND(SUM(net_amount), 2) AS net_revenue
        FROM fact_sales
        GROUP BY store_id
        ORDER BY net_revenue DESC;
    """).fetchdf()
    print(store_summary.to_string(index=False))

    # 3. Top Rejection Reasons
    print("\n" + "-"*50)
    print("DATA QUALITY AUDIT: Top Rejection Reasons")
    print("-"*50)
    rejection_summary = con.execute("""
        SELECT 
            rejection_reason,
            COUNT(*) AS count
        FROM rejected_sales_audit
        GROUP BY rejection_reason
        ORDER BY count DESC;
    """).fetchdf()
    print(rejection_summary.to_string(index=False))

    con.close()

if __name__ == "__main__":
    query_warehouse()