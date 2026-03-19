"""
MCP Client Service
Wraps Strands Agent + MCPClient to generate SQL via the embedded MCP server tools.
"""

import json
import logging
from typing import Dict, Any

from strands import Agent
from strands.tools.mcp import MCPClient
try:
    from mcp.client.streamable_http import streamable_http_client as streamablehttp_client
except ImportError:
    from mcp.client.streamable_http import streamablehttp_client

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """
You are an SQL generation agent.
Given a natural language user query, you must generate a valid SQL query by using an available SQL-extraction/generation tool.

Rules:

Always try to use a tool to generate or extract the SQL.
If no relevant tool is available, return exactly:
NO TOOL FOUND
If a tool is used, return only:
{
    "TOOL": "<tool_name>",
    "SQL": "<generated_sql_query> , output after executing the tool."
}
Do not return explanations, markdown, code fences, notes, or extra text.

SQL must be complete, executable, and aligned to the user query.
User Query: {{user_query}}
"""


class MCPClientService:
    """
    Service that connects to the in-process MCP server via HTTP,
    discovers tools, and uses a Strands Agent to pick the right tool
    and generate SQL for a user's natural-language query.
    """

    def __init__(self):
        self.mcp_url = settings.MCP_SERVER_URL
        self.model = settings.STRANDS_MODEL_ID

    def generate_sql(self, user_query: str) -> Dict[str, Any]:
        """
        Use the Strands Agent to call the MCP server's tools and produce SQL.

        Returns:
            dict with keys: tool, sql, raw_response
        """
        def transport():
            return streamablehttp_client(self.mcp_url)

        client = MCPClient(transport)
        with client:
            tools = client.list_tools_sync()
            agent = Agent(
                model=self.model,
                tools=tools,
                callback_handler=None,
            )
            prompt = SYSTEM_PROMPT.replace("{{user_query}}", user_query)
            result = agent(prompt)
            raw = str(result)

        # Try to parse the agent's JSON response
        parsed = self._parse_response(raw)
        return parsed

    def _parse_response(self, raw: str) -> Dict[str, Any]:
        """Parse the agent's raw text output into a structured dict."""
        raw = raw.strip()

        # Try direct JSON parse
        try:
            data = json.loads(raw)
            return {
                "tool": data.get("TOOL", "unknown"),
                "sql": data.get("SQL", ""),
                "raw_response": raw,
            }
        except json.JSONDecodeError:
            pass

        # If agent returned "NO TOOL FOUND"
        if "NO TOOL FOUND" in raw.upper():
            return {
                "tool": None,
                "sql": "",
                "raw_response": raw,
            }

        # Fallback: return raw text as-is
        return {
            "tool": "unknown",
            "sql": raw,
            "raw_response": raw,
        }
