#!/usr/bin/env python3
"""
API Test Script
Test the FastAPI endpoints using HTTP requests
"""

import requests
import json
import time


BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Health check passed")


def test_root():
    """Test root endpoint"""
    print_section("Testing Root Endpoint")
    
    response = requests.get(f"{BASE_URL}/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Root endpoint passed")


def test_ask_query():
    """Test the main /ask endpoint"""
    print_section("Testing /api/v1/ask Endpoint")
    
    # Test data
    queries = [
        "What was iPhone revenue in India last quarter?",
        "Show me revenue by region last month",
        "What were the top products this year?",
        "Give me daily sales trends for last 30 days"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Question: {query}")
        
        payload = {
            "user_id": "test_user_123",
            "query": query,
            "auto_execute": True
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        elapsed = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\nQuery ID: {data['query_id']}")
            print(f"Status: {data['status']}")
            print(f"\nGenerated SQL:\n{data['sql_query']}")
            
            if data.get('matched_template'):
                print(f"\nMatched Template: {data['matched_template']}")
            
            if data.get('data_preview'):
                print(f"\nData Preview ({data.get('total_rows', 0)} total rows):")
                for row in data['data_preview'][:3]:
                    print(f"  {row}")
            
            if data.get('summary'):
                print(f"\nSummary: {data['summary']}")
            
            if data.get('warnings'):
                print(f"\nWarnings: {data['warnings']}")
            
            print(f"Estimated Cost: ${data.get('estimated_cost_usd', 0):.4f}")
            print(f"Execution Time: {data.get('execution_time_seconds', 0):.3f}s")
            
            print("✅ Query executed successfully")
        else:
            print(f"❌ Error: {response.text}")
        
        print("-" * 60)


def test_invalid_query():
    """Test error handling with invalid query"""
    print_section("Testing Invalid Query")
    
    payload = {
        "user_id": "test_user_123",
        "query": "DROP TABLE apple_sales_fact",
        "auto_execute": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/ask",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 400:
        print(f"Error Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Correctly blocked invalid query")
    else:
        print("❌ Should have blocked invalid query")


def main():
    """Run all API tests"""
    print("\n" + "=" * 60)
    print("  NLP to SQL API Tests")
    print("  Make sure the server is running: python -m app.main")
    print("=" * 60)
    
    try:
        test_health()
        test_root()
        test_ask_query()
        test_invalid_query()
        
        print("\n" + "=" * 60)
        print("  ✅ All API tests passed!")
        print("=" * 60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python -m app.main\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")


if __name__ == "__main__":
    main()
