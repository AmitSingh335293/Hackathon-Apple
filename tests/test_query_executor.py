"""
Test Query Executor
Quick test of the query executor service with real Athena
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.query_executor import QueryExecutor
from app.config import get_settings
from app.utils import setup_logging, get_logger

# Setup logging
setup_logging("INFO")
logger = get_logger(__name__)


async def test_query_executor():
    """Test query executor with various queries"""
    
    settings = get_settings()
    executor = QueryExecutor()
    
    print("="*80)
    print(f"Testing Query Executor")
    print(f"Mode: {'MOCK' if settings.MOCK_MODE else 'ATHENA'}")
    print(f"Database: {settings.ATHENA_DATABASE}")
    print("="*80)
    
    # Test 1: Simple count query
    print("\n📊 TEST 1: Count total sales")
    print("-"*80)
    
    query1 = "SELECT COUNT(*) as total_sales FROM sales"
    result1 = await executor.execute_query(query1)
    
    print(f"Query: {query1}")
    print(f"Status: {result1['status']}")
    print(f"Execution Time: {result1['execution_time_seconds']}s")
    print(f"Row Count: {result1['row_count']}")
    print(f"Results: {result1['results']}")
    
    # Test 2: Sample data with limit
    print("\n📊 TEST 2: Sample sales data")
    print("-"*80)
    
    query2 = "SELECT * FROM sales LIMIT 5"
    result2 = await executor.execute_query(query2)
    
    print(f"Query: {query2}")
    print(f"Status: {result2['status']}")
    print(f"Row Count: {result2['row_count']}")
    print(f"Sample Results:")
    for i, row in enumerate(result2['results'][:3], 1):
        print(f"  Row {i}: {row}")
    
    # Test 3: Join query with aggregation
    print("\n📊 TEST 3: Revenue by product")
    print("-"*80)
    
    query3 = """
        SELECT 
            p.product_name,
            SUM(s.quantity) as units_sold,
            SUM(s.quantity * p.price) as total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY total_revenue DESC
        LIMIT 10
    """
    
    result3 = await executor.execute_query(query3)
    
    print(f"Query: {query3.strip()[:100]}...")
    print(f"Status: {result3['status']}")
    print(f"Row Count: {result3['row_count']}")
    print(f"Top Products:")
    for i, row in enumerate(result3['results'][:5], 1):
        print(f"  {i}. {row}")
    
    # Test 4: Complex join query (your use case)
    print("\n📊 TEST 4: iPhone revenue in India")
    print("-"*80)
    
    query4 = """
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
    """
    
    result4 = await executor.execute_query(query4)
    
    print(f"Query: {query4.strip()[:100]}...")
    print(f"Status: {result4['status']}")
    print(f"Row Count: {result4['row_count']}")
    print(f"Results:")
    for row in result4['results']:
        print(f"  {row}")
    
    # Test 5: Country summary
    print("\n📊 TEST 5: Revenue by country")
    print("-"*80)
    
    query5 = """
        SELECT 
            st.country,
            COUNT(DISTINCT s.sale_id) as total_orders,
            SUM(s.quantity * p.price) as total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN stores st ON s.store_id = st.store_id
        GROUP BY st.country
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    
    result5 = await executor.execute_query(query5)
    
    print(f"Query: {query5.strip()[:100]}...")
    print(f"Status: {result5['status']}")
    print(f"Row Count: {result5['row_count']}")
    print(f"Top Countries:")
    for i, row in enumerate(result5['results'], 1):
        print(f"  {i}. {row}")
    
    print("\n" + "="*80)
    print("✅ All tests completed successfully!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_query_executor())
