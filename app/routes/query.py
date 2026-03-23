"""
Query Routes
API endpoints for query operations
"""

import uuid
from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.models import (
    QueryRequest,
    QueryResponse,
    QueryStatus,
    ErrorResponse
)
from app.services import (
    QueryExecutor,
    GovernanceService,
    LLMService,
    ResultFormatter,
    MCPClientService,
    QueryValidationError
)
from app.utils import get_logger, RequestContextLogger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["queries"])


@router.post(
    "/ask",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit natural language query",
    description="Convert natural language question to SQL and optionally execute it"
)
async def ask_query(request: QueryRequest) -> QueryResponse:
    """
    Main endpoint for NLP to SQL conversion
    
    Flow:
    1. Generate SQL via MCP Client Service (Strands Agent + MCP tools)
    2. Validate query with governance
    3. Execute query (if auto_execute=True)
    4. Generate summary
    5. Return results
    """
    
    # Create request context for logging
    with RequestContextLogger(user_id=request.user_id, query=request.query) as ctx:
        
        try:
            query_id = f"q_{uuid.uuid4().hex[:12]}"
            ctx.log("info", "Processing query request", query_id=query_id)
            
            # Initialize services
            mcp_client = MCPClientService()
            governance_service = GovernanceService()
            query_executor = QueryExecutor()
            llm_service = LLMService()
            
            # Step 1: Generate SQL via MCP Client (Strands Agent picks the right tool)
            ctx.log("info", "Generating SQL via MCP tools")
            mcp_result = mcp_client.generate_sql(user_query=request.query)
            
            sql_query = mcp_result["sql"]
            tool_used = mcp_result.get("tool")
            
            if not sql_query:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not generate SQL for the given query. No matching MCP tool found."
                )
            
            metadata = {
                "generation_method": "mcp_tool",
                "mcp_tool": tool_used,
            }
            
            ctx.log(
                "info",
                "SQL generated via MCP",
                tool=tool_used,
                query_length=len(sql_query),
            )
            
            # Step 2: Validate query
            ctx.log("info", "Validating query")
            try:
                validation_result = await governance_service.validate_query(
                    sql_query=sql_query,
                    user_id=request.user_id,
                    user_permissions=None
                )
            except QueryValidationError as e:
                ctx.log("error", "Query validation failed", error=str(e))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            
            warnings = validation_result['warnings']
            estimated_cost = validation_result['estimated_cost_usd']
            
            # Step 3: Execute query (if auto_execute)
            data_preview = []
            total_rows = 0
            execution_time = None
            summary = None
            query_status = QueryStatus.PENDING_APPROVAL
            
            if request.auto_execute:
                ctx.log("info", "Executing query")
                
                exec_result = await query_executor.execute_query(
                    sql_query=sql_query,
                    query_id=query_id
                )
                
                results = exec_result['results']
                execution_time = exec_result['execution_time_seconds']
                
                # Format results
                formatted = ResultFormatter.format_results(results, preview_rows=5)
                data_preview = formatted['data_preview']
                total_rows = formatted['total_rows']
                
                ctx.log("info", "Query executed", row_count=total_rows)
                
                # Step 4: Generate summary (non-critical — don't fail the request)
                ctx.log("info", "Generating summary")
                try:
                    summary = await llm_service.generate_summary(
                        user_query=request.query,
                        sql_query=sql_query,
                        results=results
                    )
                except Exception as e:
                    ctx.log("warning", "Summary generation failed, returning results without summary", error=str(e))
                    summary = None
                    warnings.append("AI summary unavailable — results returned without summary.")
                
                query_status = QueryStatus.COMPLETED
            
            # Build response
            response = QueryResponse(
                query_id=query_id,
                user_query=request.query,
                sql_query=sql_query,
                data_preview=data_preview,
                summary=summary,
                status=query_status,
                total_rows=total_rows,
                execution_time_seconds=execution_time,
                estimated_cost_usd=estimated_cost,
                matched_template=tool_used,
                warnings=warnings,
                metadata=metadata
            )
            
            ctx.log("info", "Request completed successfully")
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            ctx.log("error", "Unexpected error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )


@router.get(
    "/queries/{query_id}",
    response_model=QueryResponse,
    summary="Get query status",
    description="Retrieve the status and results of a previously submitted query"
)
async def get_query_status(query_id: str) -> QueryResponse:
    """
    Get status of a query by ID
    
    TODO: Implement query result storage and retrieval
    Currently returns a mock response
    """
    
    # TODO: Implement query result caching in Redis/DynamoDB
    # For now, return a placeholder
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Query {query_id} not found"
    )


@router.post(
    "/queries/{query_id}/execute",
    response_model=QueryResponse,
    summary="Execute approved query",
    description="Execute a previously approved query"
)
async def execute_query(query_id: str) -> QueryResponse:
    """
    Execute a query that was previously approved but not executed
    
    TODO: Implement query state management
    """
    
    # TODO: Retrieve query from storage, validate, and execute
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Query execution endpoint not yet implemented"
    )
