"""
Standalone MCP Server runner.
Run this separately from the main FastAPI app.

Usage:
    python -m app.run_mcp
"""

import uvicorn
from app.mcp import mcp
from app.config import get_settings

settings = get_settings()

mcp_app = mcp.http_app()

if __name__ == "__main__":
    port = settings.MCP_SERVER_PORT
    print(f"Starting MCP server on port {port}...")
    uvicorn.run(
        mcp_app,
        host="0.0.0.0",
        port=port,
        log_level=settings.LOG_LEVEL.lower(),
    )
