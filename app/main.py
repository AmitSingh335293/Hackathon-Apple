"""
FastAPI Main Application
Entry point for the NLP to SQL Analytics System
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.config import get_settings
from app.utils import setup_logging, get_logger
from app.routes import query_router
from app.models import HealthResponse, ErrorResponse

# Initialize settings and logging
settings = get_settings()
setup_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Production-grade NLP to SQL Analytics System
    
    Convert natural language questions into SQL queries and execute them
    on your data lake with built-in governance and security.
    
    ## Features
    
    * **Natural Language Processing**: Ask questions in plain English
    * **SQL Generation**: Automatic SQL query generation using AWS Bedrock
    * **Template Matching**: Smart template matching for common queries
    * **Governance**: Built-in security and cost controls
    * **Execution**: Query execution on Amazon Athena
    * **Insights**: AI-generated insights from your data
    
    ## Example Request
    
    ```json
    {
        "user_id": "user_12345",
        "query": "What was iPhone revenue in India last quarter?",
        "auto_execute": true
    }
    ```
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc)
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            detail=str(exc) if settings.DEBUG else None
        ).dict()
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(
        "Application starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        mock_mode=settings.MOCK_MODE
    )
    
    # TODO: Initialize connections
    # - OpenSearch client
    # - Redis client
    # - Verify AWS credentials
    
    if settings.MOCK_MODE:
        logger.warning("Running in MOCK mode - AWS services will be simulated")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Application shutting down")
    
    # TODO: Close connections
    # - OpenSearch client
    # - Redis client


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="Health check",
    description="Check the health status of the application and its dependencies"
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint
    
    Returns the status of the application and dependent services
    """
    
    # Check service availability
    # TODO: Implement actual health checks for each service
    services = {
        "bedrock": settings.MOCK_MODE or True,  # TODO: Check Bedrock connectivity
        "opensearch": settings.MOCK_MODE or False,  # TODO: Check OpenSearch
        "athena": settings.MOCK_MODE or True,  # TODO: Check Athena
        "redis": settings.REDIS_ENABLED and False,  # TODO: Check Redis
    }
    
    overall_status = "healthy" if settings.MOCK_MODE else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        services=services
    )


# Root endpoint
@app.get(
    "/",
    tags=["system"],
    summary="Root endpoint",
    description="API information and links"
)
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }


# Include routers
app.include_router(query_router)


# Development server runner
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
