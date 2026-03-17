# NLP to SQL Analytics System - Quick Reference

## 🚀 Quick Start (No AWS Required)

### 1. Setup

```bash
# Run the quickstart script
./scripts/quickstart.sh
```

This will:
- ✅ Check Python version (3.10+ required)
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create .env file
- ✅ Run all tests
- ✅ Verify everything works

### 2. Start the API Server

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Start server
python -m app.main
```

Server will be available at: **http://localhost:8000**

### 3. Test the API

**Option A: Swagger UI (Interactive)**
- Open browser: http://localhost:8000/docs
- Try the `/api/v1/ask` endpoint

**Option B: Test Script**
```bash
python scripts/test_api.py
```

**Option C: curl**
```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "query": "What was iPhone revenue in India last quarter?",
    "auto_execute": true
  }'
```

## 📁 Project Structure

```
Hackathon-Apple/
├── app/                        # Main application
│   ├── main.py                # FastAPI app entry point
│   ├── config/
│   │   └── settings.py        # Configuration management
│   ├── models/
│   │   ├── request_models.py  # Request validation
│   │   └── response_models.py # Response schemas
│   ├── routes/
│   │   └── query.py           # API endpoints
│   ├── services/              # Business logic
│   │   ├── llm_service.py     # LLM interactions (mock)
│   │   ├── embedding_service.py    # Vector embeddings (mock)
│   │   ├── template_service.py     # Template matching
│   │   ├── query_builder.py        # SQL generation
│   │   ├── query_executor.py       # Query execution (CSV)
│   │   ├── governance_service.py   # Security validation
│   │   └── result_formatter.py     # Result formatting
│   └── utils/
│       ├── logger.py          # Structured logging
│       └── time_resolver.py   # Date parsing
├── data/
│   ├── mock/
│   │   └── apple_sales_fact.csv    # Sample data
│   └── templates/
│       └── query_templates.json    # SQL templates
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   └── services/          # API clients
│   └── package.json
├── scripts/
│   ├── quickstart.sh          # Setup script
│   └── test_api.py            # API tests
├── test_local.py              # Unit tests
├── TESTING.md                 # Testing guide
└── requirements.txt           # Python dependencies
```

## 🎯 What's Working (Mock Mode)

### ✅ Fully Functional Without AWS

All services have placeholder implementations that work locally:

| Component | Mock Implementation | Works Without AWS |
|-----------|-------------------|------------------|
| **LLM Intent Extraction** | Pattern-based parsing | ✅ |
| **LLM SQL Generation** | Template + pattern matching | ✅ |
| **LLM Summarization** | Simple text generation | ✅ |
| **Embeddings** | Hash-based vectors (1536 dims) | ✅ |
| **Vector Search** | In-memory cosine similarity | ✅ |
| **Query Execution** | Pandas on CSV data | ✅ |
| **Governance** | Full validation logic | ✅ |
| **API Endpoints** | Complete FastAPI app | ✅ |
| **Frontend** | React app with placeholders | ✅ |

### Core Features

1. **Natural Language to SQL**
   - User asks: "What was iPhone revenue in India last quarter?"
   - System generates: `SELECT SUM(revenue) FROM apple_sales_fact WHERE product='iPhone' AND region='India' AND date BETWEEN '2024-10-01' AND '2024-12-31'`

2. **Template Matching**
   - Semantic search to find similar templates
   - Parameter extraction and injection
   - Fallback to LLM generation

3. **Security & Governance**
   - Blocks forbidden keywords (DROP, DELETE, etc.)
   - Validates table access
   - Estimates query cost
   - Warns about missing WHERE clauses

4. **Query Execution**
   - Executes on local CSV data
   - Returns top 5 rows preview
   - Provides statistics

5. **Natural Language Summary**
   - Converts results back to plain English
   - Highlights key insights

## 🧪 Testing

### Run All Tests

```bash
# Unit tests (fastest)
python test_local.py

# API tests (requires server running)
python scripts/test_api.py
```

### Test Individual Components

```python
from app.services import *
import asyncio

async def test():
    # Test LLM
    llm = LLMService()
    intent = await llm.extract_intent_and_parameters(
        "What was iPhone revenue in India last quarter?"
    )
    print(intent)

asyncio.run(test())
```

## 📊 Sample Queries

Try these in the API:

```json
// Product + Region + Time
{
  "user_id": "test",
  "query": "What was iPhone revenue in India last quarter?",
  "auto_execute": true
}

// Revenue by Region  
{
  "user_id": "test",
  "query": "Show me revenue breakdown by region last month",
  "auto_execute": true
}

// Top Products
{
  "user_id": "test",
  "query": "What were the top 5 products by revenue this year?",
  "auto_execute": true
}

// Trends
{
  "user_id": "test",
  "query": "Show me daily sales trends for last 30 days",
  "auto_execute": true
}
```

## 🔧 Configuration

All configuration in `app/config/settings.py`:

```python
# Mock mode (default)
MOCK_MODE = True

# Governance limits
MAX_QUERY_ROWS = 10000
MAX_QUERY_COST_USD = 10.0
SIMILARITY_THRESHOLD = 0.75

# Allowed tables
ALLOWED_TABLES = [
    "apple_sales_fact",
    "apple_products_dim",
    "apple_regions_dim"
]

# Forbidden operations
FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "UPDATE",
    "INSERT", "TRUNCATE", "ALTER"
]
```

## 🎨 Frontend

### Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Access at: **http://localhost:5173**

### Frontend Features (Placeholders)

- Query input form
- SQL display
- Results table
- Summary display
- Query history
- Template browser

## 📝 API Endpoints

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/api/v1/ask` | POST | Submit query |
| `/api/v1/queries/{id}` | GET | Get query status (NYI) |
| `/api/v1/queries/{id}/execute` | POST | Execute approved query (NYI) |

### Example Response

```json
{
  "query_id": "q_abc123",
  "user_query": "What was iPhone revenue in India last quarter?",
  "sql_query": "SELECT SUM(revenue) as total_revenue FROM apple_sales_fact WHERE product = 'iPhone' AND region = 'India' AND date BETWEEN '2024-10-01' AND '2024-12-31'",
  "data_preview": [
    {"total_revenue": 15345000}
  ],
  "summary": "iPhone generated $15.3M in revenue in India during Q4 2024. This represents strong performance in the Indian market.",
  "status": "completed",
  "total_rows": 1,
  "execution_time_seconds": 0.045,
  "estimated_cost_usd": 0.0012,
  "matched_template": "product_revenue_by_region",
  "warnings": []
}
```

## 🔄 Incremental AWS Migration

When ready to connect to AWS:

### Step 1: Update .env

```env
MOCK_MODE=False
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

### Step 2: Configure Services

Each service automatically switches based on `MOCK_MODE`:

```python
# In llm_service.py
if not self.settings.MOCK_MODE:
    self.client = boto3.client('bedrock-runtime', ...)
else:
    self.client = None  # Use mock implementation
```

### Step 3: Set Up AWS Resources

1. **S3:** Upload data as Parquet files
2. **Glue:** Create data catalog
3. **Athena:** Configure workgroup
4. **OpenSearch:** Create cluster and index
5. **Bedrock:** Enable model access
6. **Lake Formation:** Configure permissions (optional)

### Step 4: Test Incrementally

Test each service separately:

```python
# Test Bedrock only
MOCK_MODE=False
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet...

# Test Athena only  
MOCK_MODE=False  # for execution
# Keep embeddings mocked
```

## 📚 Additional Documentation

- **[TESTING.md](TESTING.md)** - Comprehensive testing guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[API.md](docs/API.md)** - API documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Quickstart guide

## 🐛 Troubleshooting

### Module Not Found

```bash
# Make sure you're in project root
pwd  # should show .../Hackathon-Apple

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Import Errors in Tests

```bash
# Run from project root
python test_local.py  # ✅ Correct

# Don't run from subdirectories
cd app && python ../test_local.py  # ❌ Wrong
```

## 🎓 Learning Resources

### Understanding the Flow

1. User submits natural language query
2. System extracts intent (LLM)
3. Searches for matching templates (embeddings + cosine similarity)
4. Generates SQL (template or LLM)
5. Validates SQL (governance)
6. Executes query (Athena/CSV)
7. Formats results
8. Generates summary (LLM)
9. Returns response

### Key Files to Understand

1. `app/routes/query.py` - API endpoint logic
2. `app/services/query_builder.py` - SQL generation orchestration
3. `app/services/llm_service.py` - LLM mock implementations
4. `app/services/query_executor.py` - Query execution logic

## 🤝 Contributing

To add new features:

1. **New Template:** Add to `data/templates/query_templates.json`
2. **New Service:** Create in `app/services/`
3. **New Endpoint:** Add to `app/routes/`
4. **Frontend Component:** Add to `frontend/src/components/`

## 📞 Support

For issues:
1. Check TESTING.md for common problems
2. Enable debug logging: `LOG_LEVEL=DEBUG`
3. Run tests: `python test_local.py`
4. Check logs in console output
