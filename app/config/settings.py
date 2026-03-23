"""
Application Configuration
Centralized settings management using Pydantic BaseSettings
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Application
    APP_NAME: str = "NLP-to-SQL Analytics"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None  # For temporary/MFA credentials
    
    # AWS Bedrock
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    BEDROCK_EMBEDDING_MODEL_ID: str = "amazon.titan-embed-text-v1"
    BEDROCK_MAX_TOKENS: int = 2000
    BEDROCK_TEMPERATURE: float = 0.1
    
    # Amazon OpenSearch
    OPENSEARCH_HOST: str = "localhost"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_INDEX_NAME: str = "query_templates"
    OPENSEARCH_USERNAME: Optional[str] = None
    OPENSEARCH_PASSWORD: Optional[str] = None
    OPENSEARCH_USE_SSL: bool = True
    
    # Amazon Athena
    ATHENA_DATABASE: str = "apple_analytics_db"  # Updated to match setup
    ATHENA_WORKGROUP: str = "primary"
    ATHENA_OUTPUT_LOCATION: str = "s3://apple-analytics-data-lake/athena-results/"
    ATHENA_MAX_EXECUTION_TIME: int = 300  # seconds
    ATHENA_QUERY_TIMEOUT: int = 60
    
    # AWS Glue
    GLUE_CATALOG_ID: Optional[str] = None
    GLUE_DATABASE: str = "apple_analytics_db"  # Updated to match setup
    
    # AWS Lake Formation
    LAKE_FORMATION_ENABLED: bool = False
    
    # S3
    S3_DATA_BUCKET: str = "apple-analytics-data"
    S3_TEMPLATE_BUCKET: str = "apple-analytics-templates"
    
    # Redis (ElastiCache)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_TTL: int = 3600  # 1 hour
    REDIS_ENABLED: bool = False
    
    # AWS Cognito
    COGNITO_USER_POOL_ID: Optional[str] = None
    COGNITO_CLIENT_ID: Optional[str] = None
    COGNITO_REGION: Optional[str] = None
    
    # Query Governance
    MAX_QUERY_ROWS: int = 10000
    MAX_QUERY_RUNTIME_SECONDS: int = 300
    MAX_QUERY_COST_USD: float = 10.0
    ALLOWED_TABLES: list = ["sales", "products", "stores", "category", "warranty"]
    FORBIDDEN_KEYWORDS: list = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]
    
    # Template Matching
    SIMILARITY_THRESHOLD: float = 0.75
    MAX_TEMPLATE_RESULTS: int = 3
    
    # MCP Server (runs on a separate port to avoid self-deadlock)
    MCP_SERVER_PORT: int = 8001
    MCP_SERVER_URL: str = "http://localhost:8001/mcp/"
    STRANDS_MODEL_ID: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"

    AWS_BEARER_TOKEN_BEDROCK : str =""
   # Mock Mode (for testing without AWS)
    MOCK_MODE: bool = True
    MOCK_DATA_PATH: str = "data/mock/apple_sales_fact.csv"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance
    Singleton pattern ensures only one settings object
    """
    return Settings()
