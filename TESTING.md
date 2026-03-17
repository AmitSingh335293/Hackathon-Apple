# Testing Guide - NLP to SQL System

This guide explains how to test the entire system locally without any AWS dependencies.

## Prerequisites

1. Python 3.10 or higher
2. pip or poetry for dependency management

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Environment Configuration

The system is configured to run in **MOCK MODE** by default (no AWS required).

Create a `.env` file (optional):

```env
MOCK_MODE=True
LOG_LEVEL=INFO
DEBUG=True
```

## Testing Approaches

### Option 1: Unit Tests (Fastest)

Test individual components without starting the server:

```bash
python test_local.py
```

This will test:
- ✅ Embedding Service (mock embeddings)
- ✅ Template Service (semantic search)
- ✅ LLM Service (mock intent extraction & SQL generation)
- ✅ Query Builder (template matching + SQL generation)
- ✅ Governance Service (query validation)
- ✅ Query Executor (queries on mock CSV data)
- ✅ Result Formatter (data formatting)
- ✅ End-to-End Flow

**Expected output:**
```
============================================================
NLP to SQL System - Local Testing (Mock Mode)
============================================================

✅ Embedding Service test passed
✅ Template Service test passed
✅ LLM Service test passed
✅ Query Builder test passed
✅ Governance Service test passed
✅ Query Executor test passed
✅ Result Formatter test passed
✅ End-to-End test passed

============================================================
✅ All tests passed successfully!
============================================================
```

### Option 2: API Tests

Test the actual FastAPI endpoints:

**Step 1: Start the server**

```bash
python -m app.main
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload --port 8000
```

**Step 2: Run API tests** (in another terminal)

```bash
python scripts/test_api.py
```

### Option 3: Interactive API Testing

**Swagger UI (Recommended):**

1. Start the server: `python -m app.main`
2. Open browser: http://localhost:8000/docs
3. Try the `/api/v1/ask` endpoint with this sample:

```json
{
  "user_id": "test_user_123",
  "query": "What was iPhone revenue in India last quarter?",
  "auto_execute": true
}
```

**cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "query": "What was iPhone revenue in India last quarter?",
    "auto_execute": true
  }'
```

**Python requests:**

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "user_id": "test_user_123",
        "query": "What was iPhone revenue in India last quarter?",
        "auto_execute": True
    }
)

print(response.json())
```

## Sample Queries to Test

Try these natural language queries:

1. **Product + Region + Time:**
   - "What was iPhone revenue in India last quarter?"
   - "Show me iPad sales in Europe this year"

2. **Revenue by Region:**
   - "What's the revenue breakdown by region last month?"
   - "Which region had the highest sales?"

3. **Top Products:**
   - "What were the top products this year?"
   - "Show me best sellers last quarter"

4. **Trends:**
   - "Give me daily revenue trends last month"
   - "Show me sales trends this year"

5. **General Analytics:**
   - "What was total revenue last quarter?"
   - "How many units were sold in North America?"

## Understanding Mock Mode

When `MOCK_MODE=True`, the system uses:

| Service | Mock Implementation |
|---------|-------------------|
| **AWS Bedrock (LLM)** | Simple pattern matching for intent extraction and SQL generation |
| **AWS Bedrock (Embeddings)** | Hash-based deterministic embeddings (1536 dims) |
| **Amazon OpenSearch** | In-memory template search using cosine similarity |
| **Amazon Athena** | Query execution on local CSV (`data/mock/apple_sales_fact.csv`) |
| **AWS Cognito** | No authentication (accepts any user_id) |
| **Redis** | Disabled (no caching) |

## Data

### Mock Data Location

- **Sales Data:** `data/mock/apple_sales_fact.csv`
- **Templates:** `data/templates/query_templates.json`

### Mock Data Schema

```
apple_sales_fact:
  - date: DATE (YYYY-MM-DD)
  - product: VARCHAR (iPhone, iPad, Mac, Apple Watch, AirPods)
  - region: VARCHAR (North America, Europe, Asia Pacific, India, China, Japan)
  - revenue: DECIMAL (USD)
  - units_sold: INTEGER
  - customer_segment: VARCHAR (consumer, enterprise, education)
```

## Governance Rules

The system enforces these rules in mock mode:

✅ **Allowed:**
- SELECT queries
- Aggregations (SUM, COUNT, AVG)
- GROUP BY, ORDER BY, LIMIT
- WHERE clauses with date ranges

❌ **Blocked:**
- DROP, DELETE, UPDATE, INSERT, TRUNCATE, ALTER
- SELECT * without LIMIT (warning only)
- Queries without WHERE on fact tables (warning)
- Access to tables not in allowed list

## Common Issues

### 1. Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:**
```bash
# Make sure you're in the project root
cd /path/to/Hackathon-Apple

# Ensure packages are installed
pip install -r requirements.txt
```

### 2. Data File Not Found

**Problem:** `FileNotFoundError: data/mock/apple_sales_fact.csv`

**Solution:** The query executor will auto-generate sample data if file is missing, but you can also create it manually.

### 3. Port Already in Use

**Problem:** `error: Address already in use`

**Solution:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --port 8001
```

## Performance Expectations

In mock mode:

- **Query Building:** < 100ms
- **Template Search:** < 200ms
- **Query Execution:** < 50ms
- **End-to-End:** < 500ms

Real AWS mode would be:
- **Query Building:** 1-3 seconds (LLM latency)
- **Query Execution:** 5-30 seconds (Athena)

## Next Steps

Once you verify mock mode works:

1. **Add AWS Credentials** in `.env`:
   ```env
   MOCK_MODE=False
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_REGION=us-east-1
   ```

2. **Set up AWS Services:**
   - Create S3 buckets for data
   - Configure Athena workgroup
   - Set up OpenSearch cluster
   - Enable Lake Formation (optional)

3. **Update Configuration** in `app/config/settings.py`

4. **Test with real AWS** services

## Frontend Integration

Once backend is working, test with frontend:

```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:5173

## Troubleshooting

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m app.main
```

Check logs for detailed information about:
- Request processing
- SQL generation
- Template matching
- Query execution
- Validation failures

## Support

For issues or questions, check:
- `ARCHITECTURE.md` - System design
- `README.md` - Project overview
- `docs/API.md` - API documentation
