"""
Response Models
Pydantic models for API responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class QueryStatus(str, Enum):
    """Query execution status"""
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class QueryResponse(BaseModel):
    """
    Response model for /ask endpoint
    """
    query_id: str = Field(..., description="Unique identifier for this query execution")
    
    user_query: str = Field(..., description="Original natural language query")
    
    sql_query: str = Field(..., description="Generated SQL query")
    
    data_preview: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Preview of query results (top 5 rows)"
    )

    full_data: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Complete query results (all rows) — used for CSV export and email"
    )

    summary: Optional[str] = Field(
        None,
        description="Natural language summary of the results"
    )
    
    status: QueryStatus = Field(
        default=QueryStatus.PENDING_APPROVAL,
        description="Current status of the query"
    )
    
    total_rows: Optional[int] = Field(
        None,
        description="Total number of rows in the result set"
    )
    
    execution_time_seconds: Optional[float] = Field(
        None,
        description="Query execution time in seconds"
    )
    
    estimated_cost_usd: Optional[float] = Field(
        None,
        description="Estimated cost of query execution in USD"
    )
    
    matched_template: Optional[str] = Field(
        None,
        description="Name of matched query template if applicable"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="Any warnings or governance messages"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the query"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "q_abc123",
                "user_query": "What was iPhone revenue in India last quarter?",
                "sql_query": "SELECT SUM(revenue) as total_revenue FROM apple_sales_fact WHERE product = 'iPhone' AND region = 'India' AND date BETWEEN '2024-10-01' AND '2024-12-31'",
                "data_preview": [
                    {"total_revenue": 1234567.89}
                ],
                "summary": "iPhone generated $1.23M in revenue in India during Q4 2024.",
                "status": "completed",
                "total_rows": 1,
                "execution_time_seconds": 0.234,
                "estimated_cost_usd": 0.001,
                "matched_template": "revenue_by_product_region",
                "warnings": [],
                "metadata": {
                    "extracted_params": {
                        "product": "iPhone",
                        "region": "India",
                        "start_date": "2024-10-01",
                        "end_date": "2024-12-31"
                    }
                }
            }
        }


class ErrorResponse(BaseModel):
    """
    Error response model
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    query_id: Optional[str] = Field(None, description="Query ID if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Query validation failed",
                "detail": "Query contains forbidden keyword: DROP",
                "query_id": "q_abc123"
            }
        }


class HealthResponse(BaseModel):
    """
    Health check response
    """
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, bool] = Field(
        default_factory=dict,
        description="Status of dependent services"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-03-17T10:30:00Z",
                "services": {
                    "bedrock": True,
                    "opensearch": True,
                    "athena": True,
                    "redis": False
                }
            }
        }


class TemplateResponse(BaseModel):
    """
    Query template response
    """
    template_id: str
    name: str
    description: str
    sql_template: str
    parameters: List[str]
    tags: List[str]
    similarity_score: Optional[float] = None
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "tpl_123",
                "name": "revenue_by_region",
                "description": "Get revenue breakdown by region",
                "sql_template": "SELECT region, SUM(revenue) FROM apple_sales_fact WHERE date BETWEEN :start_date AND :end_date GROUP BY region",
                "parameters": ["start_date", "end_date"],
                "tags": ["revenue", "region"],
                "similarity_score": 0.89
            }
        }
