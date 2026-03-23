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

    AWS_BEARER_TOKEN_BEDROCK : str ="bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUFRQVFNNUZHWUZJTVBYNE5BJTJGMjAyNjAzMjMlMkZ1cy1lYXN0LTElMkZiZWRyb2NrJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjAzMjNUMTY1NTQ1WiZYLUFtei1FeHBpcmVzPTQzMjAwJlgtQW16LVNlY3VyaXR5LVRva2VuPUlRb0piM0pwWjJsdVgyVmpFTG4lMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkZ3RWFDWFZ6TFdWaGMzUXRNU0pHTUVRQ0lFdmc5YVpKMnBqN1RNemVaZ1REeThKUGpHZ2YzMXRVVGVGSjJISSUyQlRVQmVBaUEyY3c3aUlQdVJYcGEzenRUb2RhQXJkZVgzVFl0a1VvRUtPaWJmTVE5ZWlTck9CQWlDJTJGJTJGJTJGJTJGJTJGJTJGJTJGJTJGJTJGJTJGOEJFQUVhRERBd01URXdNRGd4T0RnMk5DSU1HV2xZb0o3NDFUSjVteTZuS3FJRTNycHIwRnZWa1VoczlMY1RFZCUyRlV2VFNMVHNsR3BscXBwaXBwclo1TFRMbnZVYzdzRjh1T01PVTREMndUeXVRVDlDYnAlMkZBazFuNXBxSlVEMk9Bc044WjN5QnczWXpicm9UYmpFWXRyWjNGUSUyRnFidjBmYkdkWFVDYlZ2aGVpYUl0TE16Tk5iS1JKYTlhbXdHUWFRa0RqazJpMlBISGEwN05DM3R6Rmo1ekM4WmxwOVJOanJaOUxUSkw3ZkJ0YTJDN2k4cEo3UHNPJTJGMmt0NWxTdHY5a2lKVHglMkY3JTJGWjQ3YUtGS2dtWFB3WTlmTWR5YUU3Y2YyV1RyYXZnJTJGWDFwNmhuaE5ubFRCdEdKaVZUempDTDREYkloMmlGdWpBOVVXeEw0c1Zrd1pUUTVzUFNXc0o3bTlRc2NDWDZsZUhCU2VTU2tDU0ptT0VaNURBeHdHR2ROTFlHSk5mcmlVM1BvSUxEQjVSZ05KNXZab1VsSjRlZUFTNXhNRWhPZDJJWDBxMXh0Z2hvSXd6RU1PRCUyRmZiNzdmdSUyQmtxaTZJVCUyRk1SNlZUNGJDeHNzdENzVCUyQkcyUENqN0dIdDNsRmIzZDI3VGJjYUtYQnpGJTJGJTJGMFJPOE8wRVcyTjh5Tm8xbnVkVFE3cVF5M3gyS2o5bng2aGNCbFhjVndCaTNKSUtmVjRUdzlsaTNvcmkyNUp0aHlPODF3NUZmczlWZHZ4aVpSd2p3SDM5bEhjRXNNSlBla1ZScUlFTiUyRk9ST1p1NFJ5blRMUEtvMUZ2amx3bHRydXpiQ3AlMkJEQVJmMVdzT056SCUyRlRnb0J0ZlJEdFlLTmpZUEJOVCUyRkR3bGxuWFVtZkJQJTJCZFZ3VSUyQk9EJTJCWVo1bVVQajBRbEpyUFElMkJsY2FDWWdSRnFPZiUyRk5ocThlMHpyQ0ZvZkNFYW12NUpIWjVTbkgwcXdtbGNJa2V5SzExeWxyeFlNWWVmdG14dTczVkhSektsJTJCJTJGUDFqTVBYZ2hjNEdPc1VDZDhJVU01WVNBN3hwa3V1V2Vyc0M2dFZPTCUyRmhyZ3YlMkIzT0V6Z0l3dVcyeFElMkJDY3YwVGd6dW5lWHVRNnJMViUyQjVFSjFUOFVvR0tMUHFwYlhSaGJjbWYzVlBISTM0aDhib3pqMUwwbTNqdnRHYkgwT1ZYZHFEekl1RDFkd3Vyakg5NHIwSUZWbWhtelZHV01uUiUyQk5tWkpXUXVYRjVZYWZQUmVHN3UxbkxHSGdNV2tPYThSU0tPT3lWTkJOaW1WR1dmU1RORmpBbyUyQkptQzJ6T1QlMkYzJTJCb2NlV1dpRGtreWlsSSUyRmswNGd1MHRLYlhtRDB5NFU4S0Ywa0ZWdHFzRjdsUlBUbG9DRGlMbHMlMkZoTHlPRVZzQks2emxZdkVSYVluM0pkM28lMkJDSjFSbU9EWmxQZzJpbFRrT2VTU2FCeDYxdkFLRGpxWWlSRUZEM3ZIdkt5RTlISGFQOWNtSW5EOW5HJTJGbDh2TDRYeFNOMCUyRlolMkJGJTJGS0VGR3hUcyUyRmVPakRlYUlZWjR6VGI3NTdBWGZ2bDhCZVVrWHl2SFEycWF5VjFsQ3RSQTBWYnpDTjFBalZubzY1bHVPcGVIUSUzRCUzRCZYLUFtei1TaWduYXR1cmU9MjA2OWEzMjRhMjliNzk0NTQxNmUyNWEzYjk1ZWI3MTUwMzc0ZWRmZmNlYzc1ZjMyMzRiNzdmZDZmZmE3OTY2MyZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmVmVyc2lvbj0x"
   # Mock Mode (for testing without AWS)
    MOCK_MODE: bool = False
    MOCK_DATA_PATH: str = "data/mock/apple_sales_fact.csv"

    # SMTP Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SMTP_USERNAME: str = "as335293@gmail.com"
    SMTP_PASSWORD: str = "ytsz xlwz paiw vogs"
    SMTP_SENDER_EMAIL: str = "as335293@gmail.com"
    SMTP_SENDER_NAME: str = "VoiceGenie AI"

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
