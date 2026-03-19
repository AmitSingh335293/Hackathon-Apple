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
        Get database schema context for SQL generation
        
        Returns:
            Schema information including tables and columns
        """
        return {
            "database": self.settings.ATHENA_DATABASE,
            "tables": {
                "sales": {
                    "description": "Fact table containing sales transactions",
                    "columns": [
                        {"name": "sale_id", "type": "STRING", "description": "Unique sale identifier"},
                        {"name": "sale_date", "type": "STRING", "description": "Sale date (YYYY-MM-DD format)"},
                        {"name": "store_id", "type": "STRING", "description": "Foreign key to stores table"},
                        {"name": "product_id", "type": "STRING", "description": "Foreign key to products table"},
                        {"name": "quantity", "type": "BIGINT", "description": "Quantity sold"}
                    ],
                    "joins": [
                        "JOIN products ON sales.product_id = products.product_id",
                        "JOIN stores ON sales.store_id = stores.store_id"
                    ]
                },
                "products": {
                    "description": "Product catalog with pricing",
                    "columns": [
                        {"name": "product_id", "type": "STRING", "description": "Primary key"},
                        {"name": "product_name", "type": "STRING", "description": "Product name (e.g., iPhone 15 Pro, MacBook Air M3)"},
                        {"name": "category_id", "type": "STRING", "description": "Foreign key to categories"},
                        {"name": "launch_date", "type": "STRING", "description": "Product launch date"},
                        {"name": "price", "type": "BIGINT", "description": "Product price in USD"}
                    ],
                    "joins": [
                        "JOIN categories ON products.category_id = categories.category_id"
                    ]
                },
                "stores": {
                    "description": "Store/location information",
                    "columns": [
                        {"name": "store_id", "type": "STRING", "description": "Primary key"},
                        {"name": "store_name", "type": "STRING", "description": "Store name (e.g., Apple Fifth Avenue)"},
                        {"name": "city", "type": "STRING", "description": "City name"},
                        {"name": "country", "type": "STRING", "description": "Country name"}
                    ]
                },
                "categories": {
                    "description": "Product categories",
                    "columns": [
                        {"name": "category_id", "type": "STRING", "description": "Primary key"},
                        {"name": "category_name", "type": "STRING", "description": "Category (iPhone, Mac, iPad, Apple Watch, AirPods, Accessories)"}
                    ]
                },
                "warranty": {
                    "description": "Warranty claims",
                    "columns": [
                        {"name": "claim_id", "type": "STRING", "description": "Primary key"},
                        {"name": "claim_date", "type": "STRING", "description": "Claim date (YYYY-MM-DD)"},
                        {"name": "sale_id", "type": "STRING", "description": "Foreign key to sales"},
                        {"name": "repair_status", "type": "STRING", "description": "Status: Completed, Rejected, Pending, In Progress"}
                    ],
                    "joins": [
                        "JOIN sales ON warranty.sale_id = sales.sale_id"
                    ]
                }
            },
            "common_patterns": [
                "Revenue: SUM(sales.quantity * products.price)",
                "Filter by product: products.product_name LIKE '%iPhone%'",
                "Filter by country: stores.country = 'India'",
                "Date range: sales.sale_date BETWEEN '2024-01-01' AND '2024-12-31'"
            ]
        }
