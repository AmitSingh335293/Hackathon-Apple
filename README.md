# NLP to SQL Analytics System

A production-grade natural language to SQL analytics system built on AWS stack. Convert business questions into SQL queries, execute them securely on your data lake, and get AI-generated insights.

## 🎯 Overview

This system enables business users to query data using natural language instead of SQL. It leverages AWS Bedrock (Claude/Titan), Amazon OpenSearch for template matching, Amazon Athena for query execution, and includes comprehensive governance and security controls.

### Key Features

- **Natural Language Processing**: Ask questions in plain English
- **Intelligent SQL Generation**: Uses AWS Bedrock LLM with schema context
- **Template Matching**: Semantic search for common query patterns
- **Security & Governance**: Built-in SQL validation, table access control, cost estimation
- **Query Execution**: Runs queries on Amazon Athena with timeout controls
- **AI Insights**: Generates natural language summaries of results
- **Production-Ready**: Docker support, structured logging, health checks

## 🏗️ Architecture

```
User Question → FastAPI → LLM (Bedrock) → SQL Generation
                  ↓
            Template Search (OpenSearch)
                  ↓
            Governance Validation
                  ↓
            Query Execution (Athena)
                  ↓
            Result Summary (LLM)
                  ↓
            Response to User
```

### Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **AI/LLM**: AWS Bedrock (Claude 3 Sonnet, Titan Embeddings)
- **Vector Search**: Amazon OpenSearch
- **Data Lake**: Amazon S3 (Parquet/Iceberg)
- **Query Engine**: Amazon Athena
- **Metadata**: AWS Glue Data Catalog
- **Governance**: AWS Lake Formation
- **Cache**: Redis (ElastiCache) - optional
- **Auth**: AWS Cognito - planned
- **Deployment**: Docker + ECS Fargate

## 📂 Project Structure

```
.
├── frontend/                   # React Frontend Application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── Header.jsx
│   │   │   ├── QueryInput.jsx
│   │   │   └── ResultDisplay.jsx
│   │   ├── pages/             # Page components
│   │   │   ├── QueryPage.jsx
│   │   │   ├── HistoryPage.jsx
│   │   │   └── TemplatesPage.jsx
│   │   ├── services/          # API and auth services
│   │   │   ├── api.js
│   │   │   └── auth.js
│   │   ├── App.jsx            # Main app component
│   │   └── main.jsx           # Entry point
│   ├── public/
│   ├── Dockerfile             # Frontend container
│   ├── nginx.conf             # Nginx configuration
│   └── package.json
├── app/                       # Backend FastAPI Application
│   ├── main.py                # FastAPI application
│   ├── config/
│   │   └── settings.py        # Configuration management
│   ├── models/
│   │   ├── request_models.py  # API request schemas
│   │   └── response_models.py # API response schemas
│   ├── routes/
│   │   └── query.py           # Query endpoints
│   ├── services/
│   │   ├── llm_service.py     # AWS Bedrock integration
│   │   ├── embedding_service.py # Text embeddings
│   │   ├── template_service.py # Template management
│   │   ├── query_builder.py  # SQL query construction
│   │   ├── query_executor.py # Athena query execution
│   │   ├── result_formatter.py # Result formatting
│   │   └── governance_service.py # Security & validation
│   └── utils/
│       ├── logger.py          # Structured logging
│       └── time_resolver.py   # Natural language date parsing
├── data/
│   ├── templates/
│   │   └── query_templates.json # SQL query templates
│   └── mock/
│       └── apple_sales_fact.csv # Sample data for testing
├── deployment/
│   └── ecs-task-definition.json # ECS Fargate config
├── Dockerfile                 # Backend container
├── docker-compose.yml         # Multi-container orchestration
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- AWS Account with Bedrock access (for production)

### Local Development (Mock Mode)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Hackathon-Apple
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and set MOCK_MODE=true for local testing
   ```

5. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. **Access the API**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment (Full Stack)

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Frontend Development

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access the frontend**
   - App: http://localhost:3000
   - Ensure backend is running on port 8000

For more frontend details, see [frontend/README.md](frontend/README.md)

## 📝 API Usage

### Ask a Query

**Endpoint**: `POST /api/v1/ask`

**Request**:
```json
{
  "user_id": "user_12345",
  "query": "What was iPhone revenue in India last quarter?",
  "auto_execute": true
}
```

**Response**:
```json
{
  "query_id": "q_abc123def456",
  "user_query": "What was iPhone revenue in India last quarter?",
  "sql_query": "SELECT SUM(revenue) as total_revenue FROM apple_sales_fact WHERE product = 'iPhone' AND region = 'India' AND date BETWEEN '2024-10-01' AND '2024-12-31'",
  "data_preview": [
    {
      "total_revenue": 509500.00
    }
  ],
  "summary": "iPhone generated $509,500 in revenue in India during Q4 2024, representing strong performance in the region.",
  "status": "completed",
  "total_rows": 1,
  "execution_time_seconds": 0.145,
  "estimated_cost_usd": 0.001,
  "matched_template": "product_revenue_by_region",
  "warnings": [],
  "metadata": {
    "generation_method": "template",
    "intent_data": {
      "product": "iPhone",
      "region": "India",
      "time_period": "last quarter"
    }
  }
}
```

### Example Queries

Try these natural language questions:

- "What was iPhone revenue in India last quarter?"
- "Show me top products by revenue this year"
- "Compare sales by region for last month"
- "What's the revenue trend for iPad by month?"
- "Show revenue by customer segment"

## ⚙️ Configuration

### Environment Variables

Key configuration options (see `.env.example` for full list):

```bash
# Mock Mode (for local testing without AWS)
MOCK_MODE=true

# AWS Credentials
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Bedrock Models
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1

# Athena Configuration
ATHENA_DATABASE=apple_analytics
ATHENA_OUTPUT_LOCATION=s3://your-bucket/results/

# Governance
MAX_QUERY_COST_USD=10.0
MAX_QUERY_ROWS=10000
```

## 🔒 Security & Governance

The system includes multiple security layers:

### SQL Validation
- Blocks forbidden keywords (DROP, DELETE, UPDATE, etc.)
- Prevents `SELECT *` queries
- Validates table access
- Requires LIMIT clauses

### Access Control
- Table-level permissions
- User-based restrictions
- AWS Lake Formation integration (optional)

### Cost Controls
- Estimates query cost before execution
- Blocks expensive queries
- Configurable cost thresholds

### Query Limits
- Maximum execution time: 300 seconds
- Maximum rows: 10,000
- Timeout enforcement

## 📊 Query Templates

Templates enable efficient pattern matching for common queries. See `data/templates/query_templates.json`.

Example template:
```json
{
  "name": "product_revenue_by_region",
  "description": "Get revenue for a specific product in a specific region",
  "sql_template": "SELECT product, region, SUM(revenue) as total_revenue FROM apple_sales_fact WHERE product = :product AND region = :region AND date BETWEEN :start_date AND :end_date GROUP BY product, region",
  "parameters": ["product", "region", "start_date", "end_date"]
}
```

## 🧪 Testing

### Mock Mode

The system includes a mock mode for testing without AWS services:

```bash
# Set in .env
MOCK_MODE=true
MOCK_DATA_PATH=data/mock/apple_sales_fact.csv
```

Mock mode provides:
- Simulated LLM responses
- Local CSV query execution
- Mock embeddings for template matching

### Sample Data

Sample dataset includes:
- Apple product sales (iPhone, iPad, Mac, Apple Watch, AirPods)
- Multiple regions (North America, Europe, Asia Pacific, India, China, Japan)
- Time range: Jan 2024 - Dec 2024
- Customer segments: consumer, enterprise, education

## 🚢 AWS Deployment

### ECS Fargate Deployment

1. **Build and push Docker image**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
   
   # Build image
   docker build -t nlp-sql-analytics .
   
   # Tag and push
   docker tag nlp-sql-analytics:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/nlp-sql-analytics:latest
   docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/nlp-sql-analytics:latest
   ```

2. **Create ECS Service**
   ```bash
   aws ecs register-task-definition --cli-input-json file://deployment/ecs-task-definition.json
   ```

3. **Configure Load Balancer** (Application Load Balancer)
   - Target port: 8000
   - Health check: `/health`

### Required AWS Resources

- **S3 Bucket**: Data storage and Athena results
- **Glue Data Catalog**: Table metadata
- **Athena Workgroup**: Query execution
- **OpenSearch Domain**: Template storage
- **ElastiCache Redis**: Query caching (optional)
- **ECR Repository**: Docker images
- **ECS Cluster**: Container orchestration
- **Application Load Balancer**: Traffic distribution
- **Secrets Manager**: Credentials storage

## 📈 Monitoring & Logging

### Structured Logging

All logs are in JSON format with:
- Request ID tracking
- Execution time
- User context
- Error details

### Health Checks

- **Endpoint**: `GET /health`
- **Checks**: Bedrock, OpenSearch, Athena, Redis connectivity

### Metrics to Track

- Query latency
- LLM token usage
- Athena scan costs
- Template match rate
- Error rates

## 🛠️ Development

### Adding New Templates

1. Edit `data/templates/query_templates.json`
2. Add template with description and SQL
3. Restart application to reload

### Extending Services

Each service is independently testable:
- `LLMService`: Bedrock integration
- `EmbeddingService`: Text embeddings
- `TemplateService`: Template management
- `QueryBuilder`: SQL construction
- `QueryExecutor`: Query execution
- `GovernanceService`: Security validation

## 🔮 Future Enhancements

- [ ] Redis caching for repeated queries
- [ ] Conversation context memory
- [ ] Feedback loop for template improvement
- [ ] Multi-turn conversations
- [ ] Query result export (CSV, JSON, Parquet)
- [ ] Advanced visualizations
- [ ] Query history and favorites
- [ ] Admin dashboard for monitoring
- [ ] A/B testing for LLM prompts

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 👥 Contributors

Built with ❤️ for Apple Hackathon 2026

---

For questions or support, please open an issue in the repository.