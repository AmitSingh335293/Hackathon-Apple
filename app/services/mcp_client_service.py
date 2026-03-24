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
You are an SQL generation agent for Apple Retail Sales data on Amazon Athena (Trino SQL dialect).
Given a natural language user query, you must generate a valid SQL query by using an available SQL-extraction/generation tool.

=== DATABASE SCHEMA (apple_analytics_db) ===

TABLE: sales  (Fact table, ~1M rows, alias: s)
  sale_id     STRING  PK   -- e.g. 'YG-8782'
  sale_date   STRING       -- format: DD-MM-YYYY (e.g. '16-06-2023'). Parse with: date_parse(sale_date, '%d-%m-%Y')
  store_id    STRING  FK → stores.Store_ID
  product_id  STRING  FK → products.Product_ID
  quantity    BIGINT       -- range: 1-10

TABLE: products  (Dimension, 89 products, alias: p)
  Product_ID    STRING  PK   -- e.g. 'P-1'
  Product_Name  STRING       -- e.g. 'iPhone 14 Pro', 'MacBook Air (M2)', 'AirPods Pro'
  Category_ID   STRING  FK → category.category_id  -- e.g. 'CAT-1'
  Launch_Date   STRING       -- format: YYYY-MM-DD. Compare with: CAST(Launch_Date AS DATE)
  Price         BIGINT       -- range: 231-1965 (USD)

TABLE: stores  (Dimension, 75 stores, alias: st)
  Store_ID    STRING  PK   -- e.g. 'ST-1'
  Store_Name  STRING       -- e.g. 'Apple Fifth Avenue'
  City        STRING       -- 47 cities
  Country     STRING       -- 19 countries

TABLE: category  (Dimension, 10 categories, alias: c)
  category_id    STRING  PK  -- e.g. 'CAT-1'
  category_name  STRING      -- Accessories, Audio, Desktop, Laptop, Smart Speaker, Smartphone, Streaming Device, Subscription Service, Tablet, Wearable

TABLE: warranty  (30K claims, alias: w)
  claim_id       STRING  PK   -- e.g. 'CL-58750'
  claim_date     STRING        -- format: YYYY-MM-DD. Parse with: date_parse(claim_date, '%Y-%m-%d')
  sale_id        STRING  FK → sales.sale_id
  repair_status  STRING        -- Completed, Pending, In Progress, Rejected

=== JOIN PATHS ===
  sales → products:    s.product_id = p.Product_ID
  sales → stores:      s.store_id = st.Store_ID
  products → category: p.Category_ID = c.category_id
  warranty → sales:    w.sale_id = s.sale_id

=== TRINO/ATHENA SQL RULES ===
  1. sale_date (DD-MM-YYYY) → date_parse(s.sale_date, '%d-%m-%Y')
  2. claim_date (YYYY-MM-DD) → date_parse(w.claim_date, '%Y-%m-%d')
  3. Launch_Date (YYYY-MM-DD) → CAST(p.Launch_Date AS DATE)
  4. Date literals: DATE '2023-01-01'
  5. Use date_format(), year(), quarter(), date_diff('day', start, end)
  6. NEVER use MySQL: STR_TO_DATE, DATEDIFF, YEAR(), QUARTER()
  7. Column names are CASE-SENSITIVE — use exact case from schema above
  8. Revenue = s.quantity * p.Price
  9. category_name is in the "category" table, NOT in "products"
  10. Only SELECT queries. No INSERT/UPDATE/DELETE/DROP.

=== RULES ===
Always try to use a predefined tool (Q01-Q15) first. Only use generate_sql when no predefined tool fits.
If no relevant tool is available, return exactly: NO TOOL FOUND
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
