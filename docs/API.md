# API Documentation

Complete API reference for the NLP to SQL Analytics System.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

**Status**: Authentication is planned using AWS Cognito but not yet implemented.

For now, all endpoints require a `user_id` in the request body.

## Endpoints

### 1. Submit Natural Language Query

Convert a natural language question into SQL and optionally execute it.

**Endpoint**: `POST /api/v1/ask`

**Request Body**:
```json
{
  "user_id": "string (required, 1-100 chars)",
  "query": "string (required, 5-500 chars)",
  "context": "object (optional)",
  "auto_execute": "boolean (optional, default: false)"
}
```

**Response**: `200 OK`
```json
{
  "query_id": "string",
  "user_query": "string",
  "sql_query": "string",
  "data_preview": "array",
  "summary": "string | null",
  "status": "pending_approval | completed | failed",
  "total_rows": "integer | null",
  "execution_time_seconds": "float | null",
  "estimated_cost_usd": "float | null",
  "matched_template": "string | null",
  "warnings": "array of strings",
  "metadata": "object"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error or query violates governance policies
- `500 Internal Server Error`: Unexpected error

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "query": "What was iPhone revenue in India last quarter?",
    "auto_execute": true
  }'
```

**Example Response**:
```json
{
  "query_id": "q_abc123",
  "user_query": "What was iPhone revenue in India last quarter?",
  "sql_query": "SELECT SUM(revenue) as total_revenue FROM apple_sales_fact WHERE product = 'iPhone' AND region = 'India' AND date BETWEEN '2024-10-01' AND '2024-12-31'",
  "data_preview": [
    {"total_revenue": 509500.00}
  ],
  "summary": "iPhone generated $509,500 in revenue in India during Q4 2024.",
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

### 2. Get Query Status

Retrieve the status of a previously submitted query.

**Endpoint**: `GET /api/v1/queries/{query_id}`

**Path Parameters**:
- `query_id`: Query identifier (string)

**Response**: `200 OK` (same as submit query)

**Error Responses**:
- `404 Not Found`: Query ID not found

**Status**: Not yet implemented - returns 404

### 3. Execute Approved Query

Execute a query that was previously approved but not executed.

**Endpoint**: `POST /api/v1/queries/{query_id}/execute`

**Path Parameters**:
- `query_id`: Query identifier (string)

**Response**: `200 OK` (same as submit query)

**Error Responses**:
- `404 Not Found`: Query ID not found
- `501 Not Implemented`: Endpoint not yet implemented

**Status**: Not yet implemented - returns 501

## System Endpoints

### Health Check

Check the health status of the application and its dependencies.

**Endpoint**: `GET /health`

**Response**: `200 OK`
```json
{
  "status": "healthy | degraded",
  "version": "string",
  "timestamp": "ISO 8601 datetime",
  "services": {
    "bedrock": "boolean",
    "opensearch": "boolean",
    "athena": "boolean",
    "redis": "boolean"
  }
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

### Root Information

Get API information and links.

**Endpoint**: `GET /`

**Response**: `200 OK`
```json
{
  "name": "NLP-to-SQL Analytics",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/health",
  "api": "/api/v1"
}
```

## Interactive Documentation

The API includes auto-generated interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Query Examples

### Revenue by Product

```json
{
  "user_id": "user_001",
  "query": "Show me iPhone revenue for 2024",
  "auto_execute": true
}
```

### Regional Analysis

```json
{
  "user_id": "user_001",
  "query": "Compare sales by region last month",
  "auto_execute": true
}
```

### Top Products

```json
{
  "user_id": "user_001",
  "query": "What are the top 5 products by revenue?",
  "auto_execute": true
}
```

### Time-based Trends

```json
{
  "user_id": "user_001",
  "query": "Show iPad sales trend by month this year",
  "auto_execute": true
}
```

### Customer Segmentation

```json
{
  "user_id": "user_001",
  "query": "Show revenue breakdown by customer segment",
  "auto_execute": true
}
```

## Query Status Values

- `pending_approval`: SQL generated, awaiting user approval
- `approved`: Query approved but not yet executed
- `executing`: Query currently running
- `completed`: Query executed successfully
- `failed`: Query execution failed
- `rejected`: Query rejected by governance policies

## Governance Rules

Queries are validated against these rules:

### Forbidden Keywords
- DROP
- DELETE
- UPDATE
- INSERT
- TRUNCATE
- ALTER

### Required Constraints
- Must not use `SELECT *`
- Must include LIMIT clause for fact tables
- Must not exceed cost threshold ($10 USD by default)
- Must only access allowed tables

### Allowed Tables
- `apple_sales_fact`
- `apple_products_dim`
- `apple_regions_dim`

## Error Handling

All errors follow this format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "detail": "Optional detailed information",
  "query_id": "Optional query ID if available"
}
```

### Common Error Types

- `ValidationError`: Request validation failed
- `QueryValidationError`: Query violates governance policies
- `ExecutionError`: Query execution failed
- `InternalServerError`: Unexpected server error

## Rate Limits

**Status**: Not yet implemented

Future implementation will include:
- Per-user rate limits
- Cost-based throttling
- Concurrent query limits

## Monitoring

All requests are logged with:
- Request ID (UUID)
- User ID
- Query text (truncated)
- Execution time
- Status code
- Errors (if any)

Logs are in structured JSON format for easy parsing and analysis.
