"""
Query Builder Service
Constructs SQL queries from templates or generates new ones
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.config import get_settings
from app.utils import get_logger, TimeResolver
from app.services.llm_service import LLMService
from app.services.template_service import TemplateService

logger = get_logger(__name__)
settings = get_settings()


class QueryBuilder:
    """
    Builds SQL queries by either:
    1. Using matched templates with parameter injection
    2. Generating new SQL using LLM with schema context
    """
    
    def __init__(self):
        """Initialize query builder with dependencies"""
        self.settings = settings
        self.llm_service = LLMService()
        self.template_service = TemplateService()
        self.time_resolver = TimeResolver()
    
    async def build_query(
        self,
        user_query: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Build SQL query from natural language
        
        Args:
            user_query: Natural language question
            user_id: User identifier for access control
        
        Returns:
            Dictionary with SQL query and metadata
        """
        logger.info("Building query", query=user_query[:100])
        
        # Step 1: Extract intent and parameters using LLM
        intent_data = await self.llm_service.extract_intent_and_parameters(user_query)
        logger.info("Intent extracted", intent=intent_data.get('intent'))
        
        # Step 2: Search for similar templates
        similar_templates = await self.template_service.search_similar_templates(
            user_query,
            top_k=self.settings.MAX_TEMPLATE_RESULTS
        )
        
        matched_template = None
        sql_query = None
        
        # Step 3: Try to use template if found
        if similar_templates:
            best_match = similar_templates[0]
            similarity = best_match.get('similarity_score', 0)
            
            if similarity >= self.settings.SIMILARITY_THRESHOLD:
                logger.info(
                    "Template matched",
                    template=best_match['name'],
                    similarity=similarity
                )
                
                try:
                    sql_query = await self._apply_template(
                        best_match,
                        user_query,
                        intent_data
                    )
                    matched_template = best_match['name']
                except Exception as e:
                    logger.warning("Failed to apply template", error=str(e))
                    sql_query = None
        
        # Step 4: Generate SQL using LLM if no template matched
        if not sql_query:
            logger.info("Generating SQL using LLM")
            schema_context = self._get_schema_context()
            sql_query = await self.llm_service.generate_sql(
                user_query,
                schema_context,
                intent_data
            )
        
        # Step 5: Extract query metadata
        metadata = {
            "intent_data": intent_data,
            "matched_template": matched_template,
            "template_similarity": similar_templates[0].get('similarity_score') if similar_templates else None,
            "generation_method": "template" if matched_template else "llm"
        }
        
        return {
            "sql_query": sql_query,
            "metadata": metadata
        }
    
    async def _apply_template(
        self,
        template: Dict[str, Any],
        user_query: str,
        intent_data: Dict[str, Any]
    ) -> str:
        """
        Apply template by injecting parameters
        
        Args:
            template: Template dictionary
            user_query: Original user query
            intent_data: Extracted intent and parameters
        
        Returns:
            SQL query with parameters injected
        """
        sql_template = template['sql_template']
        required_params = template.get('parameters', [])
        
        # Extract parameter values
        params = await self._extract_parameters(user_query, intent_data, required_params)
        
        # Inject parameters into template
        sql_query = self._inject_parameters(sql_template, params)
        
        logger.info("Template applied", params=params)
        return sql_query
    
    async def _extract_parameters(
        self,
        user_query: str,
        intent_data: Dict[str, Any],
        required_params: List[str]
    ) -> Dict[str, Any]:
        """
        Extract parameter values from query and intent data
        
        Args:
            user_query: User's natural language query
            intent_data: Extracted intent information
            required_params: List of required parameter names
        
        Returns:
            Dictionary of parameter values
        """
        params = {}
        
        # Extract time parameters
        time_params = self.time_resolver.extract_time_parameters(user_query)
        if time_params:
            params['start_date'] = time_params.get('start_date')
            params['end_date'] = time_params.get('end_date')
        
        # Extract from intent data
        if intent_data.get('product'):
            params['product'] = intent_data['product']
        
        if intent_data.get('region'):
            params['region'] = intent_data['region']
        
        # Set defaults for missing required parameters
        for param in required_params:
            if param not in params:
                params[param] = self._get_default_parameter_value(param)
        
        return params
    
    def _inject_parameters(self, sql_template: str, params: Dict[str, Any]) -> str:
        """
        Inject parameters into SQL template
        
        Args:
            sql_template: SQL template with :param_name placeholders
            params: Dictionary of parameter values
        
        Returns:
            SQL with parameters injected
        """
        sql = sql_template
        
        for param_name, param_value in params.items():
            placeholder = f":{param_name}"
            
            # Quote string values
            if isinstance(param_value, str):
                param_value = f"'{param_value}'"
            elif param_value is None:
                param_value = "NULL"
            
            sql = sql.replace(placeholder, str(param_value))
        
        return sql
    
    def _get_default_parameter_value(self, param_name: str) -> Any:
        """Get default value for a parameter"""
        defaults = {
            'start_date': '2024-01-01',
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'limit': 1000
        }
        return defaults.get(param_name)
    
    def _get_schema_context(self) -> Dict[str, Any]:
        """
        Get database schema context for SQL generation.
        Matches the actual Apple Retail Sales dataset exactly.
        
        Returns:
            Schema information including tables, columns, relationships,
            sample values, and Athena/Trino-specific SQL rules.
        """
        return {
            "database": self.settings.ATHENA_DATABASE,
            "engine": "Amazon Athena (Trino/Presto SQL engine)",
            "tables": {
                "sales": {
                    "description": "Core transactional fact table — every individual sale across 75 global Apple retail stores. 1,040,200 rows.",
                    "columns": [
                        {"name": "sale_id", "type": "STRING", "key": "PK", "description": "Unique sale identifier", "format": "XX-NNNNN (e.g. YG-8782, QX-999001)"},
                        {"name": "sale_date", "type": "STRING", "description": "Sale date stored as DD-MM-YYYY string. MUST use date_parse(sale_date, '%d-%m-%Y') to convert for any date filtering or formatting.", "format": "DD-MM-YYYY (e.g. 16-06-2023, 13-04-2022)"},
                        {"name": "store_id", "type": "STRING", "key": "FK → stores.Store_ID", "description": "Store identifier", "format": "ST-N (e.g. ST-10, ST-63)"},
                        {"name": "product_id", "type": "STRING", "key": "FK → products.Product_ID", "description": "Product identifier", "format": "P-N (e.g. P-38, P-48)"},
                        {"name": "quantity", "type": "INTEGER", "description": "Units sold per transaction. Range: 1-10."}
                    ]
                },
                "products": {
                    "description": "Product dimension/catalog — 89 Apple products across 10 categories with pricing.",
                    "columns": [
                        {"name": "Product_ID", "type": "STRING", "key": "PK", "description": "Product identifier", "format": "P-N (e.g. P-1, P-2)"},
                        {"name": "Product_Name", "type": "STRING", "description": "Apple product name", "sample_values": ["MacBook", "MacBook Air (M1)", "MacBook Air (M2)", "MacBook Pro 13-inch", "iPhone 15", "iPhone 15 Pro", "iPad Air", "AirPods Pro", "Apple Watch Series 9", "iMac", "Apple TV 4K", "HomePod mini"]},
                        {"name": "Category_ID", "type": "STRING", "key": "FK → category.category_id", "description": "Category identifier", "format": "CAT-N (e.g. CAT-1, CAT-2)"},
                        {"name": "Launch_Date", "type": "STRING", "description": "Product launch date in YYYY-MM-DD format", "format": "YYYY-MM-DD (e.g. 2023-09-17)"},
                        {"name": "Price", "type": "INTEGER", "description": "Product price in USD (integer)", "sample_values": ["149", "768", "1149", "1783"]}
                    ]
                },
                "stores": {
                    "description": "Store dimension — 75 Apple retail stores across 19 countries and 47 cities.",
                    "columns": [
                        {"name": "Store_ID", "type": "STRING", "key": "PK", "description": "Store identifier", "format": "ST-N (e.g. ST-1, ST-2)"},
                        {"name": "Store_Name", "type": "STRING", "description": "Official store name", "sample_values": ["Apple Fifth Avenue", "Apple Union Square", "Apple Michigan Avenue", "Apple Regent Street"]},
                        {"name": "City", "type": "STRING", "description": "City name", "sample_values": ["New York", "San Francisco", "Chicago", "Los Angeles", "London", "Tokyo", "Shanghai"]},
                        {"name": "Country", "type": "STRING", "description": "Country name (19 countries)", "allowed_values": ["Australia", "Austria", "Canada", "China", "Colombia", "France", "Germany", "Italy", "Japan", "Mexico", "Netherlands", "Singapore", "South Korea", "Spain", "Taiwan", "Thailand", "UAE", "United Kingdom", "United States"]}
                    ]
                },
                "category": {
                    "description": "Product category lookup — 10 Apple product categories. NOTE: table name is 'category' (singular), NOT 'categories'.",
                    "columns": [
                        {"name": "category_id", "type": "STRING", "key": "PK", "description": "Category identifier", "format": "CAT-N (e.g. CAT-1, CAT-2)"},
                        {"name": "category_name", "type": "STRING", "description": "Category name", "allowed_values": ["Laptop", "Audio", "Tablet", "Smartphone", "Wearable", "Streaming Device", "Desktop", "Subscription Service", "Smart Speaker", "Accessories"]}
                    ]
                },
                "warranty": {
                    "description": "Warranty claims — 30,000 claims (~2.88% of sales). Not all sales have warranty claims.",
                    "columns": [
                        {"name": "claim_id", "type": "STRING", "key": "PK", "description": "Claim identifier", "format": "CL-NNNNN (e.g. CL-58750)"},
                        {"name": "claim_date", "type": "STRING", "description": "Claim date in YYYY-MM-DD format", "format": "YYYY-MM-DD (e.g. 2024-01-30)"},
                        {"name": "sale_id", "type": "STRING", "key": "FK → sales.sale_id", "description": "Sale transaction this claim is against"},
                        {"name": "repair_status", "type": "STRING", "description": "Repair status", "allowed_values": ["Completed", "Pending", "In Progress", "Rejected"]}
                    ]
                }
            },
            "relationships": [
                "sales.product_id = products.Product_ID",
                "sales.store_id = stores.Store_ID",
                "products.Category_ID = category.category_id",
                "warranty.sale_id = sales.sale_id"
            ],
            "join_examples": [
                "sales s JOIN products p ON s.product_id = p.Product_ID",
                "sales s JOIN stores st ON s.store_id = st.Store_ID",
                "products p JOIN category c ON p.Category_ID = c.category_id",
                "warranty w JOIN sales s ON w.sale_id = s.sale_id"
            ],
            "common_query_patterns": [
                "Revenue calculation: SUM(s.quantity * p.Price)",
                "Filter by product: p.Product_Name = 'iPhone 15' (use exact name, case-sensitive)",
                "Filter by country: st.Country = 'United States' (use full country name from allowed_values)",
                "Filter by category: c.category_name = 'Smartphone' (use exact name from allowed_values)",
                "Date filtering: date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE '2024-01-01' AND DATE '2024-12-31'",
                "Extract year: year(date_parse(s.sale_date, '%d-%m-%Y'))",
                "Extract month: date_format(date_parse(s.sale_date, '%d-%m-%Y'), '%Y-%m')",
                "Warranty join: warranty w JOIN sales s ON w.sale_id = s.sale_id JOIN products p ON s.product_id = p.Product_ID"
            ],
            "athena_trino_sql_rules": [
                "CRITICAL: sale_date is stored as DD-MM-YYYY string. Always use date_parse(s.sale_date, '%d-%m-%Y') before any date comparison, extraction, or formatting.",
                "Use DATE 'YYYY-MM-DD' literals for date comparisons (e.g., DATE '2024-01-01'), not bare strings.",
                "Use date_format(date_parse(...), '<pattern>') for formatting dates in output.",
                "Use year(), month(), day() functions on parsed dates for extraction.",
                "Column names are CASE-SENSITIVE: products uses PascalCase (Product_ID, Product_Name, Category_ID, Launch_Date, Price), stores uses PascalCase (Store_ID, Store_Name, City, Country), sales uses lowercase (sale_id, sale_date, store_id, product_id, quantity), category uses lowercase (category_id, category_name), warranty uses lowercase (claim_id, claim_date, sale_id, repair_status).",
                "Table name is 'category' (singular), NOT 'categories'.",
                "String comparisons are case-sensitive in Athena/Trino. Match exact casing from allowed_values.",
                "Use LIMIT to cap result rows (max 1000).",
                "Do NOT use ILIKE — use lower() with LIKE for case-insensitive matching if needed.",
                "Use ROUND(value, N) for decimal rounding.",
                "Use COALESCE() to handle NULLs in calculations.",
                "Warranty claims exist for only ~2.88% of sales — use LEFT JOIN when you need all sales including those without claims.",
                "Do NOT end SQL with a semicolon.",
                "Do NOT use AS keyword for table aliases — use: FROM sales s (not FROM sales AS s).",
                "Do NOT use double quotes for string literals — use single quotes only.",
                "CONCAT() or || operator for string concatenation — not +."
            ]
        }
