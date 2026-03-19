"""
Test Athena Queries
Run sample queries against your data lake
"""

import boto3
import time
import pandas as pd
from pathlib import Path

# Configuration
DATABASE = "apple_analytics_db"
OUTPUT_LOCATION = "s3://apple-analytics-data-lake/athena-results/"
REGION = "us-east-1"

# Initialize Athena client
athena_client = boto3.client('athena', region_name=REGION)


def run_query(query: str, wait_for_results: bool = True):
    """
    Execute Athena query and optionally wait for results
    
    Args:
        query: SQL query to execute
        wait_for_results: Whether to wait and fetch results
    
    Returns:
        Query execution ID and results (if wait_for_results=True)
    """
    print(f"\n{'='*80}")
    print(f"QUERY:\n{query}")
    print(f"{'='*80}")
    
    # Start query execution
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': DATABASE},
        ResultConfiguration={'OutputLocation': OUTPUT_LOCATION}
    )
    
    query_execution_id = response['QueryExecutionId']
    print(f"Query ID: {query_execution_id}")
    
    if not wait_for_results:
        return query_execution_id, None
    
    # Wait for query to complete
    while True:
        response = athena_client.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        
        state = response['QueryExecution']['Status']['State']
        
        if state == 'SUCCEEDED':
            print(f"✅ Query completed successfully")
            
            # Get statistics
            stats = response['QueryExecution']['Statistics']
            data_scanned_mb = stats.get('DataScannedInBytes', 0) / (1024 * 1024)
            execution_time_ms = stats.get('EngineExecutionTimeInMillis', 0)
            cost_estimate = (data_scanned_mb / 1024) * 5  # $5 per TB
            
            print(f"   Data scanned: {data_scanned_mb:.2f} MB")
            print(f"   Execution time: {execution_time_ms/1000:.2f} seconds")
            print(f"   Estimated cost: ${cost_estimate:.6f}")
            
            break
        elif state == 'FAILED':
            error = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
            print(f"❌ Query failed: {error}")
            return query_execution_id, None
        elif state == 'CANCELLED':
            print(f"⚠️  Query was cancelled")
            return query_execution_id, None
        
        time.sleep(1)
    
    # Fetch results
    results = athena_client.get_query_results(
        QueryExecutionId=query_execution_id,
        MaxResults=100
    )
    
    # Parse results into DataFrame
    columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = []
    
    for row in results['ResultSet']['Rows'][1:]:  # Skip header row
        rows.append([field.get('VarCharValue', '') for field in row['Data']])
    
    df = pd.DataFrame(rows, columns=columns)
    
    print(f"\n📊 RESULTS ({len(df)} rows):")
    print(df.to_string(index=False))
    
    return query_execution_id, df


def main():
    """Run test queries"""
    
    print("🧪 Testing Athena Queries")
    print(f"Database: {DATABASE}")
    print(f"Region: {REGION}\n")
    
    # Test 1: List tables
    print("\n" + "="*80)
    print("TEST 1: List Tables")
    print("="*80)
    run_query("SHOW TABLES;")
    
    # Test 2: Count records
    print("\n" + "="*80)
    print("TEST 2: Count Records per Table")
    print("="*80)
    run_query("""
        SELECT 'sales' as table_name, COUNT(*) as row_count FROM sales
        UNION ALL
        SELECT 'products', COUNT(*) FROM products
        UNION ALL
        SELECT 'stores', COUNT(*) FROM stores
        UNION ALL
        SELECT 'categories', COUNT(*) FROM categories
        UNION ALL
        SELECT 'warranty', COUNT(*) FROM warranty
    """)
    
    # Test 3: Sample join
    print("\n" + "="*80)
    print("TEST 3: Sample Data with Joins")
    print("="*80)
    run_query("""
        SELECT 
            s.sale_id,
            s.sale_date,
            p.product_name,
            c.category_name,
            st.city,
            st.country,
            s.quantity,
            p.price,
            s.quantity * p.price as revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        JOIN stores st ON s.store_id = st.store_id
        LIMIT 10
    """)
    
    # Test 4: Top products by revenue
    print("\n" + "="*80)
    print("TEST 4: Top 10 Products by Revenue")
    print("="*80)
    run_query("""
        SELECT 
            p.product_name,
            c.category_name,
            SUM(s.quantity) as units_sold,
            SUM(s.quantity * p.price) as total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        GROUP BY p.product_name, c.category_name
        ORDER BY total_revenue DESC
        LIMIT 10
    """)
    
    # Test 5: Revenue by country
    print("\n" + "="*80)
    print("TEST 5: Revenue by Country")
    print("="*80)
    run_query("""
        SELECT 
            st.country,
            COUNT(DISTINCT s.sale_id) as total_orders,
            SUM(s.quantity) as units_sold,
            SUM(s.quantity * p.price) as total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN stores st ON s.store_id = st.store_id
        GROUP BY st.country
        ORDER BY total_revenue DESC
        LIMIT 10
    """)
    
    # Test 6: iPhone revenue in India
    print("\n" + "="*80)
    print("TEST 6: iPhone Revenue in India (Use Case Example)")
    print("="*80)
    run_query("""
        SELECT 
            p.product_name,
            st.country,
            SUM(s.quantity) as units_sold,
            SUM(s.quantity * p.price) as revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN stores st ON s.store_id = st.store_id
        WHERE 
            p.product_name LIKE '%iPhone%'
            AND st.country = 'India'
        GROUP BY p.product_name, st.country
        ORDER BY revenue DESC
    """)
    
    # Test 7: Warranty claim analysis
    print("\n" + "="*80)
    print("TEST 7: Warranty Claims by Product")
    print("="*80)
    run_query("""
        SELECT 
            p.product_name,
            w.repair_status,
            COUNT(w.claim_id) as claim_count,
            ROUND(COUNT(w.claim_id) * 100.0 / 
                  (SELECT COUNT(*) FROM warranty), 2) as pct_of_total
        FROM warranty w
        JOIN sales s ON w.sale_id = s.sale_id
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_name, w.repair_status
        ORDER BY claim_count DESC
        LIMIT 15
    """)
    
    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)


if __name__ == "__main__":
    main()
