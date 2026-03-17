# ARCHITECTURE DOCUMENTATION

## NLP to SQL Analytics System - Full Stack Architecture

This document provides a comprehensive overview of the system architecture, component interactions, and design decisions.

---

## 1. System Overview

The NLP to SQL Analytics System is a full-stack application that enables business users to query data lakes using natural language. The system consists of:

- **Frontend**: React-based web application
- **Backend**: FastAPI REST API server
- **AI/ML**: AWS Bedrock for LLM and embeddings
- **Data Layer**: Amazon S3, Athena, Glue Catalog
- **Vector Search**: Amazon OpenSearch
- **Cache**: Redis (optional)
- **Auth**: AWS Cognito (planned)

---

## 2. Frontend Architecture

### Technology Stack
- **Framework**: React 18 with Vite
- **Routing**: React Router v6
- **API Client**: Axios
- **Styling**: CSS modules
- **Build**: Vite
- **Deployment**: Nginx in Docker

### Component Structure

```
QueryPage (Main Interface)
├── QueryInput (Natural Language Input)
└── ResultDisplay (SQL + Data + Insights)

HistoryPage (Query History)
└── QueryHistoryList (Past Queries)

TemplatesPage (Template Browser)
└── TemplateList (Available Templates)
```

### State Management
- **Local State**: React useState for component-level state
- **API State**: Axios for async data fetching
- **Auth State**: AWS Amplify (to be implemented)

### API Integration
The frontend communicates with the backend via REST API:
- `POST /api/v1/ask` - Submit natural language query
- `GET /api/v1/history/{user_id}` - Fetch query history
- `GET /api/v1/templates` - List available templates

---

## 3. Backend Architecture

### Service Layer Design

```
┌─────────────────────────────────────────────────┐
│              FastAPI Application                │
└─────────────────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │     Query Router          │
        │  (routes/query.py)        │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴─────────────────────┐
        │                                   │
   ┌────▼─────┐                      ┌────▼─────┐
   │   LLM    │                      │  Template│
   │ Service  │                      │  Service │
   └────┬─────┘                      └────┬─────┘
        │                                  │
        │         ┌──────────────┐        │
        └────────►│ Query Builder│◄───────┘
                  └──────┬───────┘
                         │
                  ┌──────▼─────────┐
                  │  Governance    │
                  │  Validation    │
                  └──────┬─────────┘
                         │
                  ┌──────▼─────────┐
                  │ Query Executor │
                  │   (Athena)     │
                  └──────┬─────────┘
                         │
                  ┌──────▼─────────┐
                  │   Result       │
                  │  Formatter     │
                  └────────────────┘
```

### Service Responsibilities

#### 1. **LLM Service** (`llm_service.py`)
- Communicates with AWS Bedrock
- Extracts intent and parameters from natural language
- Generates SQL queries using Claude 3
- Creates natural language summaries
- Handles prompt engineering

#### 2. **Embedding Service** (`embedding_service.py`)
- Generates vector embeddings using AWS Titan
- Integrates with OpenSearch for similarity search
- Manages embedding cache

#### 3. **Template Service** (`template_service.py`)
- Loads and manages SQL templates
- Performs semantic search for template matching
- Extracts parameters from natural language
- Injects parameters into templates

#### 4. **Query Builder** (`query_builder.py`)
- Constructs SQL queries from templates
- Applies filters and parameters
- Handles time resolution
- Validates SQL syntax

#### 5. **Governance Service** (`governance_service.py`)
- Validates SQL queries against rules
- Checks table access permissions
- Estimates query cost and runtime
- Prevents dangerous operations (e.g., SELECT *)
- Enforces row limits

#### 6. **Query Executor** (`query_executor.py`)
- Executes queries on Amazon Athena
- Polls for query completion
- Handles timeouts and errors
- Retrieves results from S3

#### 7. **Result Formatter** (`result_formatter.py`)
- Formats query results for API response
- Limits preview rows
- Converts data types
- Generates metadata

---

## 4. Data Flow

### Query Processing Flow

```
1. User Input
   ├─→ "What was iPhone revenue in India last quarter?"
   │
2. Frontend (QueryPage)
   ├─→ POST /api/v1/ask
   │
3. Backend Router
   ├─→ Authenticate user (future: Cognito)
   ├─→ Generate request ID
   ├─→ Log request
   │
4. Embedding Service
   ├─→ Generate query embedding
   ├─→ Search OpenSearch for similar templates
   │
5. Decision Branch
   ├─→ IF template found:
   │   ├─→ LLM extracts parameters
   │   ├─→ Template Service injects parameters
   │   └─→ SQL generated from template
   │
   └─→ ELSE:
       ├─→ LLM Service gets schema context
       ├─→ LLM generates SQL from scratch
       └─→ SQL returned
   │
6. Governance Service
   ├─→ Validate SQL syntax
   ├─→ Check table permissions
   ├─→ Estimate cost
   ├─→ Apply row limits
   │
7. Query Executor (if auto_execute=true)
   ├─→ Submit to Athena
   ├─→ Poll for completion
   ├─→ Fetch results from S3
   │
8. Result Formatter
   ├─→ Format top 5 rows
   ├─→ Generate summary via LLM
   │
9. Response
   └─→ {
       "sql_query": "SELECT ...",
       "data_preview": [...],
       "summary": "iPhone revenue in India...",
       "status": "completed"
   }
```

---

## 5. AWS Integration

### AWS Services Used

#### AWS Bedrock
- **Models**:
  - `anthropic.claude-3-sonnet-v1` - SQL generation, parameter extraction
  - `amazon.titan-embed-text-v1` - Text embeddings
- **Features**:
  - Streaming responses
  - Token-based pricing
  - No infrastructure management

#### Amazon Athena
- **Use Cases**:
  - SQL query execution on S3 data
  - Supports Parquet, ORC, Iceberg formats
  - Serverless, pay-per-query
- **Features**:
  - Query result caching
  - Cost controls
  - Workgroup isolation

#### Amazon OpenSearch
- **Use Cases**:
  - Vector similarity search for template matching
  - Semantic search across queries
- **Indices**:
  - `query-templates` - Store template embeddings
  - `query-history` - Store past queries (future)

#### AWS Glue Data Catalog
- **Use Cases**:
  - Schema discovery
  - Table metadata
  - Column descriptions for LLM context

#### AWS S3
- **Buckets**:
  - `data-lake-bucket` - Parquet/Iceberg tables
  - `athena-results-bucket` - Query results

#### AWS Lake Formation
- **Features**:
  - Fine-grained access control
  - Column-level security
  - Audit logging

#### AWS Cognito (Planned)
- **Use Cases**:
  - User authentication
  - JWT token issuance
  - User pool management

---

## 6. Security & Governance

### Query Validation Rules
1. **Syntax Validation**: Ensure SQL is syntactically correct
2. **Table Whitelist**: Only allow querying approved tables
3. **Operation Restrictions**:
   - No `DELETE`, `UPDATE`, `DROP`
   - No `SELECT *` (must specify columns)
4. **Cost Estimation**: Warn if query exceeds cost threshold
5. **Row Limits**: Enforce `LIMIT` clause
6. **Timeout Controls**: Cancel long-running queries

### Access Control
- **User-based permissions**: Map user_id to allowed tables
- **Column masking**: Hide sensitive columns based on role
- **Audit logging**: Log all queries and access

---

## 7. Deployment Architecture

### Docker Compose (Local/Dev)

```yaml
Services:
- frontend (Port 3000)
  - Nginx serving React build
  - Proxies /api to backend

- backend (Port 8000)
  - FastAPI application
  - Mock mode for local testing

- redis (Port 6379) [Optional]
  - Query result caching
  - Session storage

- opensearch (Port 9200) [Optional]
  - Vector search
  - Template matching
```

### ECS Fargate (Production)

```
Application Load Balancer
├─→ Target Group: Frontend (Port 3000)
│   └─→ ECS Service: nlp-sql-frontend
│       └─→ Task: 2 containers (min)
│
└─→ Target Group: Backend (Port 8000)
    └─→ ECS Service: nlp-sql-backend
        └─→ Task: 4 containers (min)
```

#### Infrastructure Components
- **VPC**: 2 public, 2 private subnets
- **NAT Gateway**: For private subnet internet access
- **Security Groups**:
  - Frontend: Allow 3000 from ALB
  - Backend: Allow 8000 from frontend
- **CloudWatch**: Logs and metrics
- **Parameter Store**: Configuration secrets

---

## 8. Caching Strategy

### Redis Cache Layers

1. **Query Results Cache**
   - Key: `query:hash:{sha256(sql)}`
   - Value: Query results JSON
   - TTL: 1 hour

2. **Embedding Cache**
   - Key: `embedding:{sha256(text)}`
   - Value: Vector array
   - TTL: 24 hours

3. **Template Cache**
   - Key: `templates:all`
   - Value: All templates JSON
   - TTL: Invalidate on update

---

## 9. Monitoring & Observability

### Metrics
- Request count by endpoint
- Average query execution time
- LLM API latency
- Cache hit rate
- Error rate by type

### Logging
- Structured JSON logs
- Request ID tracking
- Query SQL logging
- Error stack traces

### Alerts
- High error rate (> 5%)
- Slow query execution (> 30s)
- AWS Bedrock quota exceeded
- Athena query failures

---

## 10. Future Enhancements

### Phase 2
- [ ] AWS Cognito authentication
- [ ] Query history persistence
- [ ] Real-time query status via WebSocket
- [ ] Data visualization (charts)
- [ ] Export to CSV/Excel

### Phase 3
- [ ] Conversation context memory
- [ ] Multi-turn query refinement
- [ ] Saved dashboards
- [ ] Scheduled queries
- [ ] Email alerts

### Phase 4
- [ ] Multi-model support (GPT-4, Gemini)
- [ ] Custom data connectors
- [ ] API rate limiting
- [ ] Multi-tenancy

---

## 11. Development Guidelines

### Code Standards
- **Python**: PEP 8, type hints, docstrings
- **JavaScript**: ESLint, Prettier
- **Git**: Conventional commits

### Testing Strategy
- **Backend**: pytest, 80% coverage target
- **Frontend**: Vitest, React Testing Library
- **E2E**: Playwright
- **Load Testing**: Locust

### CI/CD Pipeline
1. Code commit
2. Lint and format check
3. Unit tests
4. Build Docker images
5. Integration tests
6. Deploy to staging
7. Smoke tests
8. Deploy to production

---

## 12. Cost Optimization

### Estimated Monthly Costs (1000 queries/day)

| Service | Usage | Cost |
|---------|-------|------|
| AWS Bedrock | 30k requests | ~$150 |
| Amazon Athena | 100 GB scanned | ~$5 |
| OpenSearch | t3.small | ~$35 |
| ECS Fargate | 2 vCPU, 4GB RAM | ~$60 |
| ElastiCache | cache.t3.micro | ~$15 |
| S3 Storage | 1 TB | ~$23 |
| **Total** | | **~$288/month** |

### Optimization Tips
- Use query result caching aggressively
- Partition data in S3 by date
- Use columnar formats (Parquet)
- Implement LLM response caching
- Use Athena workgroups for cost controls

---

## Contact

For questions or contributions, please contact the development team.
