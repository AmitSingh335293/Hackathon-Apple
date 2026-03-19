#!/bin/bash

# Test Query Executor
# Tests the query execution service with real Athena or mock data

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "🧪 Testing Query Executor Service"
echo ""

# Check if .env exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Please create .env with your AWS credentials"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)

# Check mode
if [ "$MOCK_MODE" = "true" ]; then
    echo "🔧 Running in MOCK mode (no AWS required)"
else
    echo "☁️  Running with real AWS Athena"
    echo "   Database: $ATHENA_DATABASE"
    echo "   Region: $AWS_REGION"
fi

echo ""
echo "Starting tests..."
echo "="

# Run test from project root
cd "$PROJECT_ROOT"
python tests/test_query_executor.py

echo ""
echo "✅ Test completed"
