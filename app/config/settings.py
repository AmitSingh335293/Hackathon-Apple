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

    AWS_BEARER_TOKEN_BEDROCK : str ="bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUFRQVFNNUZHWU83VjJHTDZTJTJGMjAyNjAzMjMlMkZ1cy1lYXN0LTElMkZiZWRyb2NrJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjAzMjNUMTUwMzIxWiZYLUFtei1FeHBpcmVzPTQzMjAwJlgtQW16LVNlY3VyaXR5LVRva2VuPUlRb0piM0pwWjJsdVgyVmpFTGYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkZ3RWFDWFZ6TFdWaGMzUXRNU0pJTUVZQ0lRRGZhZ2xvQWYlMkJHeXRkQTklMkZKbGhLa1ltWmNLQ2ZEdllWNFN2eTBYZUtkTlpRSWhBSnJRTlVEWTNEOEJ1bGdscFFSSTJIY1JFY3JmYWJvR3I3all0dXUlMkZmUWVES3N3RUNJRCUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRndFUUFSb01NREF4TVRBd09ERTRPRFkwSWd3TzglMkI2aVZGbWpwVkVwdXYwcW9BU2lpb2h0UjBwYUVkcGxVU1N4Q2ZCZ2xRa0tzTUZxWU1MZGRTZjB1c29HJTJCR2NIV3d5bFZEOTNFOWhEMTdzSW5uaklOVSUyQjRVT0FCSzlVSDVoYm51Y0F1T2VLblU2akxhekt1UThIdEUwVFJIOWklMkZrWU5mdXpHcTZTRWZGb0lvJTJGNWxUWVBkRnBTUiUyRmNzT2s4T3ZRN3AlMkZhaHdmeExDQ2FjJTJCTGdnbVdabjY3S0M3UW1aTWxBMk1MUmp6eHlHeCUyRkFoWkxxaHk0OXhSZXlIV25HNDlSSXRSMzI2SFdESmVuRUJ0TWhEOEJXakR6eDRHZk1rS2ZxcEVVN3dTbHRlRTBvJTJCOHV6cDRvcCUyRlNLVWhlaHJGaVVkN0hFOE9OQmFnOXp4ZmliNGp2cUklMkJKSWw1ZXBjOWF5QXdvNWZ5alQ0TDNvYzdzenZ4Z0dIYkNvWWt5dUswMGMlMkJQZW1xJTJGRFQxMTNwUjZmN1J1SEdtQSUyRnNkRm5qQjZiNm5iMzFpTGpBejlHUGEyV0YwamhrUnd0bWxvQTNScm5RNUppdEVna0h6WVd0dUNGaFVOb1I1czJDTXhYVUQlMkZIT1lPSDhvNkFLJTJCMzlyYnBpRnNVUThWZ202OFAlMkI5RGllSWJ6RUtnY0pSNEZGNWhvYlZCcjluZ2VnTCUyRnZwV3BJcHFzUzRhWTVKdDZSOEZiTkpOYXBEb09vd0c3SkNqcXpHOWlHakNLc2tDTCUyRmZMY25RS1FKYWxURFYyZEVYT1NONlExUFRoVVVRcE1KWWh4UENYMUZJRGxoYXBnNlZUUDNUeldPcSUyRjZ4TlVVc1dFc0w4UHM1YkQ0N1M2a2l0b0Q2WHJlUW5RJTJGdFJzWmRhN0NMYlpycEFwVFl3d0VVbEtmRCUyQkxSRWhxJTJCSWZSNjc4NUttUEZoVHJBJTJGMmRSY2xvJTJGcUJtZG5KV1BudEp0JTJCeCUyQmNDRDFFM1RQVzdsVGVGM3hFM0s0VVcxbzhVTUt1cWhjNEdPc01DUlJDRnJmcHIlMkJKbTlzWDNyNzlScmlteTlXYUlWeE5PZEp0MGxGbnZHdzB4MUZpWEFIaGpBNEhtckRHdW5VVTQwMiUyQm54bGxud2I4Y3hpYmFxdExjY0syTTdTazdNMGtqQmc0UXpWSUdXWVRTZmNjRUVuQjU2ZTlDYXVVbW1EJTJGJTJGbElZWEpGUEVubUpPQkI1bTE4RnJXRmpJUHdzYXlVQWZ2YzZiM1puUFZFN0FQa01zbmJwT1RsZnRjJTJCNkNFTGpUaHRwUkJiOHdZQWxJbEhNc1g1THI4MUg3UDV1enVUcWpHS1kxM2dhRXNTb0NLeFNTJTJGWVY0SGVYVWNPSXFQVCUyRkJ2TUx0alIxRWlkd2FIcVl0dUN5Q21WVXhySGwyT0JPeXVyd3JaY0s0UEJEV3c4aVNZeldtdHFkcnhpUE9nUmNEaTFaWUVENUNyTHphUUVNWndMTnp4aUt2Sm9UUUw4eUpOUGlLMUtwQm5idjRpckRUSUdwSEp5aTdpb3Z0dkgxJTJGRzNuc0w3anRJJTJCd3BmcFZGUVBVT1lDZGJmUlNSQklhUjhnYWNSeU53R3VSdm5RYmMlM0QmWC1BbXotU2lnbmF0dXJlPWJiZTc3NDNlYzQ2M2Y0MjFmMDAyYTA5ODYwOTM1NmQ3OTg2NmYwMzkxMTkxMDZkZWNjMWNiMjI4YmNlNGY3MzImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JlZlcnNpb249MQ=="
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
