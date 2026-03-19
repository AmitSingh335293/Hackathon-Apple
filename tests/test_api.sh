#!/bin/bash

# Quick test script for the NLP to SQL API
# Tests basic functionality in mock mode

set -e

API_URL=${API_URL:-http://localhost:8000}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Testing NLP to SQL Analytics API"
echo "API URL: $API_URL"
echo "================================"
echo

# Test 1: Health Check
echo "Test 1: Health Check"
response=$(curl -s ${API_URL}/health)
if echo $response | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi
echo

# Test 2: Root endpoint
echo "Test 2: Root Endpoint"
response=$(curl -s ${API_URL}/)
if echo $response | grep -q "running"; then
    echo -e "${GREEN}✓ Root endpoint passed${NC}"
else
    echo -e "${RED}✗ Root endpoint failed${NC}"
    exit 1
fi
echo

# Test 3: Simple query
echo "Test 3: iPhone Revenue Query"
response=$(curl -s -X POST ${API_URL}/api/v1/ask \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": "test_user",
        "query": "What was iPhone revenue in India last quarter?",
        "auto_execute": true
    }')

if echo $response | grep -q "query_id"; then
    echo -e "${GREEN}✓ Query execution passed${NC}"
    echo "Response preview:"
    echo $response | python3 -m json.tool | head -20
else
    echo -e "${RED}✗ Query execution failed${NC}"
    echo $response
    exit 1
fi
echo

# Test 4: Regional revenue query
echo "Test 4: Regional Revenue Query"
response=$(curl -s -X POST ${API_URL}/api/v1/ask \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": "test_user",
        "query": "Show me revenue by region",
        "auto_execute": true
    }')

if echo $response | grep -q '"status":"completed"'; then
    echo -e "${GREEN}✓ Regional query passed${NC}"
else
    echo -e "${RED}✗ Regional query failed${NC}"
    exit 1
fi
echo

# Test 5: Invalid query (should fail validation)
echo "Test 5: Invalid Query (DROP table)"
response=$(curl -s -X POST ${API_URL}/api/v1/ask \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": "test_user",
        "query": "DROP TABLE apple_sales_fact",
        "auto_execute": false
    }')

if echo $response | grep -q "forbidden"; then
    echo -e "${GREEN}✓ Security validation passed${NC}"
else
    echo -e "${RED}✗ Security validation failed${NC}"
    exit 1
fi
echo

echo "================================"
echo -e "${GREEN}All tests passed! ✓${NC}"
