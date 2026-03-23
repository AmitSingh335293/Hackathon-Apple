"""
LLM Service
Handles interactions with AWS Bedrock for text generation
"""

import json
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError

from app.config import get_settings
from app.utils import get_logger

logger = get_logger(__name__)
settings = get_settings()


# Topics/keywords that indicate a query is relevant to Apple retail sales data
ALLOWED_TOPICS = [
    "sale", "sales", "revenue", "units", "quantity", "sold",
    "product", "iphone", "ipad", "mac", "macbook", "airpods", "apple watch",
    "homepod", "apple tv", "imac", "accessories", "apple",
    "store", "stores", "region", "country", "city",
    "warranty", "claim", "repair", "pending", "rejected",
    "category", "laptop", "audio", "tablet", "smartphone", "wearable",
    "streaming", "desktop", "subscription", "speaker",
    "price", "cost", "average", "total", "count", "trend", "growth",
    "quarter", "month", "year", "date", "period",
    "top", "best", "worst", "highest", "lowest", "most", "least",
    "compare", "comparison", "performance", "profit", "order",
]

DATABASE_CONTEXT = """This system only answers questions about Apple retail sales data.
The database contains these tables:
- sales: transactional sales data (sale_id, sale_date, store_id, product_id, quantity)
- products: Apple product catalog (Product_ID, Product_Name, Category_ID, Launch_Date, Price)
- stores: Apple retail store locations (Store_ID, Store_Name, City, Country) across 19 countries
- category: product categories (category_id, category_name) — Laptop, Audio, Tablet, Smartphone, Wearable, Streaming Device, Desktop, Subscription Service, Smart Speaker, Accessories
- warranty: warranty claims (claim_id, claim_date, sale_id, repair_status)

Only queries related to these tables and Apple retail analytics are allowed."""


class LLMService:
    """
    Service for interacting with AWS Bedrock LLM models
    Provides intent extraction, SQL generation, and result summarization
    """
    
    def __init__(self):
        """Initialize Bedrock client"""
        self.settings = settings
        
        if not self.settings.MOCK_MODE:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=self.settings.AWS_REGION,
                aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY
            )
        else:
            self.client = None
            logger.info("LLM Service running in MOCK mode")
    
    async def validate_query_relevance(self, user_query: str) -> Dict[str, Any]:
        """
        Check whether the user query is relevant to Apple retail sales data.
        Rejects off-topic queries (e.g. weather, general knowledge, coding help).

        Returns:
            Dict with keys:
              - is_relevant (bool)
              - rejection_message (str | None): friendly message if not relevant
        """
        query_lower = user_query.lower()

        # Quick keyword check — if any allowed topic appears, likely relevant
        if any(topic in query_lower for topic in ALLOWED_TOPICS):
            return {"is_relevant": True, "rejection_message": None}

        # If no keyword matched, use LLM for a more nuanced check
        if not self.settings.MOCK_MODE:
            prompt = f"""You are a strict query-relevance classifier for an Apple Retail Sales analytics bot.

{DATABASE_CONTEXT}

User query: "{user_query}"

Determine if this query is asking about Apple retail sales data, products, stores, warranty claims, or any analytics that can be answered from the tables above.

Respond with ONLY a JSON object:
{{"is_relevant": true}} or {{"is_relevant": false, "reason": "brief reason"}}"""

            try:
                response = await self._invoke_model(prompt, max_tokens=100)
                result = self._parse_json_response(response)
                if result.get("is_relevant"):
                    return {"is_relevant": True, "rejection_message": None}
                reason = result.get("reason", "")
                return {
                    "is_relevant": False,
                    "rejection_message": (
                        f"Sorry, I can only answer questions about Apple retail sales data "
                        f"(sales, products, stores, categories, and warranty claims). "
                        f"{reason}"
                    ),
                }
            except Exception as e:
                logger.warning("LLM relevance check failed, falling back to rejection", error=str(e))

        # Fallback: no keyword match and either mock mode or LLM call failed → reject
        return {
            "is_relevant": False,
            "rejection_message": (
                "Sorry, I can only answer questions about Apple retail sales data — "
                "including sales transactions, products (iPhone, iPad, Mac, etc.), "
                "store locations, product categories, and warranty claims. "
                "Please rephrase your question to relate to Apple retail analytics."
            ),
        }

    async def extract_intent_and_parameters(self, user_query: str) -> Dict[str, Any]:
        """
        Extract intent and parameters from natural language query
        
        Args:
            user_query: Natural language question
        
        Returns:
            Dictionary containing intent, entities, and parameters
        """
        prompt = f"""You are a SQL query assistant for Apple sales analytics.
Extract the following from the user's question:
1. Intent: What type of analysis (e.g., revenue, units sold, trends, comparison)
2. Product: Product name if mentioned (iPhone, iPad, Mac, etc.)
3. Region: Geographic region if mentioned
4. Time period: Time range mentioned
5. Metrics: What metrics to calculate (revenue, units, growth, etc.)
6. Aggregation: How to group the data (by region, by product, by time, etc.)

User Question: "{user_query}"

Respond in JSON format with these keys: intent, product, region, time_period, metrics, aggregation.
Use null for missing values."""

        if self.settings.MOCK_MODE:
            return self._mock_extract_intent(user_query)
        
        try:
            response = await self._invoke_model(prompt)
            result = self._parse_json_response(response)
            logger.info("Intent extracted successfully", intent=result.get("intent"))
            return result
        except Exception as e:
            logger.error("Failed to extract intent", error=str(e))
            raise
    
    async def generate_sql(
        self,
        user_query: str,
        schema_context: Dict[str, Any],
        intent_data: Dict[str, Any]
    ) -> str:
        """
        Generate SQL query from natural language using schema context
        
        Args:
            user_query: Natural language question
            schema_context: Database schema information
            intent_data: Extracted intent and parameters
        
        Returns:
            Generated SQL query string
        """
        prompt = f"""You are an expert SQL query generator for Apple sales analytics using Amazon Athena.

Database Schema:
{json.dumps(schema_context, indent=2)}

User Intent:
{json.dumps(intent_data, indent=2)}

User Question: "{user_query}"

Generate a valid SQL query that:
1. Uses only the tables and columns from the schema
2. Follows Athena/Presto SQL syntax
3. Includes appropriate WHERE clauses for filtering
4. Uses proper aggregations (SUM, COUNT, AVG, etc.)
5. Includes GROUP BY and ORDER BY where appropriate
6. Limits results to 1000 rows maximum
7. Uses date format 'YYYY-MM-DD'

Return ONLY the SQL query, no explanations."""

        if self.settings.MOCK_MODE:
            return self._mock_generate_sql(user_query, intent_data)
        
        try:
            sql_query = await self._invoke_model(prompt)
            sql_query = self._clean_sql_output(sql_query)
            logger.info("SQL generated successfully", query_length=len(sql_query))
            return sql_query
        except Exception as e:
            logger.error("Failed to generate SQL", error=str(e))
            raise
    
    async def generate_summary(
        self,
        user_query: str,
        sql_query: str,
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate natural language summary of query results
        
        Args:
            user_query: Original user question
            sql_query: Executed SQL query
            results: Query results (top rows)
        
        Returns:
            Natural language summary
        """
        prompt = f"""You are a business analyst summarizing data for Apple executives.

User Question: "{user_query}"

SQL Query Executed:
{sql_query}

Results (top rows):
{json.dumps(results[:5], indent=2)}

Provide a concise 2-3 sentence summary that:
1. Directly answers the user's question
2. Highlights key insights from the data
3. Uses business-friendly language (no SQL jargon)
4. Includes specific numbers and percentages where relevant

Summary:"""

        if self.settings.MOCK_MODE:
            return self._mock_generate_summary(user_query, results)
        
        try:
            summary = await self._invoke_model(prompt, max_tokens=300)
            logger.info("Summary generated successfully")
            return summary.strip()
        except Exception as e:
            logger.error("Failed to generate summary", error=str(e))
            raise
    
    async def _invoke_model(self, prompt: str, max_tokens: int = None) -> str:
        """
        Invoke Bedrock model with the given prompt
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
        
        Returns:
            Model response text
        """
        max_tokens = max_tokens or self.settings.BEDROCK_MAX_TOKENS
        
        # Claude 3 Sonnet format
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": self.settings.BEDROCK_TEMPERATURE,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        try:
            response = self.client.invoke_model(
                modelId=self.settings.BEDROCK_MODEL_ID,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
        
        except ClientError as e:
            logger.error("Bedrock API error", error=str(e))
            raise
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from model response, handling markdown code blocks"""
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        return json.loads(response.strip())
    
    def _clean_sql_output(self, sql: str) -> str:
        """Clean SQL output from model, removing markdown and extra text"""
        sql = sql.strip()
        
        # Remove markdown code blocks
        if sql.startswith("```sql"):
            sql = sql[6:]
        elif sql.startswith("```"):
            sql = sql[3:]
        
        if sql.endswith("```"):
            sql = sql[:-3]
        
        # Remove any trailing semicolon
        sql = sql.strip().rstrip(';')
        
        return sql.strip()
    
    # Mock implementations for testing without AWS
    def _mock_extract_intent(self, user_query: str) -> Dict[str, Any]:
        """Mock intent extraction for testing"""
        query_lower = user_query.lower()
        
        return {
            "intent": "revenue_analysis" if "revenue" in query_lower else "sales_analysis",
            "product": "iPhone" if "iphone" in query_lower else None,
            "region": "India" if "india" in query_lower else None,
            "time_period": "last quarter" if "last quarter" in query_lower else None,
            "metrics": ["revenue"] if "revenue" in query_lower else ["units_sold"],
            "aggregation": ["region"] if "by region" in query_lower else ["product"]
        }
    
    def _mock_generate_sql(self, user_query: str, intent_data: Dict[str, Any]) -> str:
        """Mock SQL generation for testing"""
        query_lower = user_query.lower()
        
        if "iphone" in query_lower and "india" in query_lower:
            return """SELECT SUM(revenue) as total_revenue, SUM(units_sold) as total_units
FROM apple_sales_fact
WHERE product = 'iPhone'
  AND region = 'India'
  AND date BETWEEN '2024-10-01' AND '2024-12-31'"""
        
        return """SELECT region, product, SUM(revenue) as total_revenue
FROM apple_sales_fact
WHERE date >= '2024-01-01'
GROUP BY region, product
ORDER BY total_revenue DESC
LIMIT 10"""
    
    def _mock_generate_summary(self, user_query: str, results: List[Dict[str, Any]]) -> str:
        """Mock summary generation for testing"""
        if not results:
            return "No data found for the specified criteria."
        
        first_result = results[0]
        if 'total_revenue' in first_result:
            revenue = first_result['total_revenue']
            return f"Based on the analysis, the total revenue was ${revenue:,.2f}. This represents the performance for the specified period and criteria."
        
        return "The query returned results as requested. The top results show the most relevant data points based on your question."
