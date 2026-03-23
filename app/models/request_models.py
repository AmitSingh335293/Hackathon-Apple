"""
Request Models
Pydantic models for API request validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List


class QueryRequest(BaseModel):
    """
    Request model for /ask endpoint
    """
    user_id: str = Field(
        ...,
        description="Unique identifier for the user making the request",
        min_length=1,
        max_length=100,
        example="user_12345"
    )
    
    query: str = Field(
        ...,
        description="Natural language question to convert to SQL",
        min_length=5,
        max_length=500,
        example="What was iPhone revenue in India last quarter?"
    )
    
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context for query resolution (optional)"
    )
    
    auto_execute: bool = Field(
        default=False,
        description="Whether to automatically execute the query without approval"
    )
    
    @validator('query')
    def validate_query(cls, v):
        """Validate query is not empty after stripping whitespace"""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "query": "What was iPhone revenue in India last quarter?",
                "auto_execute": False
            }
        }


class FeedbackRequest(BaseModel):
    """
    Request model for query feedback
    """
    query_id: str = Field(..., description="ID of the executed query")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "q_abc123",
                "rating": 5,
                "feedback": "Perfect results!"
            }
        }


class TemplateCreateRequest(BaseModel):
    """
    Request model for creating a new query template
    """
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    sql_template: str = Field(..., min_length=10)
    parameters: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "revenue_by_region",
                "description": "Get revenue breakdown by region for a time period",
                "sql_template": "SELECT region, SUM(revenue) as total_revenue FROM apple_sales_fact WHERE date BETWEEN :start_date AND :end_date GROUP BY region ORDER BY total_revenue DESC",
                "parameters": ["start_date", "end_date"],
                "tags": ["revenue", "region", "sales"]
            }
        }


class EmailRequest(BaseModel):
    """
    Request model for /send-email endpoint.
    SMTP credentials are read from server-side .env — only recipients and content are needed.
    """
    recipient_emails: List[str] = Field(..., description="List of recipient email addresses", min_length=1)
    subject: str = Field("Query Results — VoiceGenie AI", description="Email subject line")
    body: str = Field("Please find the query results attached as a CSV file.", description="Plain-text email body")
    csv_content: str = Field(..., description="Raw CSV content to attach")
    csv_filename: str = Field("query_results.csv", description="Filename for the CSV attachment")

    class Config:
        json_schema_extra = {
            "example": {
                "recipient_emails": ["colleague@example.com", "manager@example.com"],
                "subject": "iPhone Revenue Data",
                "body": "Hi,\n\nPlease find the query results attached.\n\nBest,\nVoiceGenie AI",
                "csv_content": "product,revenue\niPhone,100000",
                "csv_filename": "query_results.csv"
            }
        }

