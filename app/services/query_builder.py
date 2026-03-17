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
                "apple_sales_fact": {
                    "description": "Fact table containing Apple product sales data",
                    "columns": [
                        {"name": "date", "type": "DATE", "description": "Transaction date"},
                        {"name": "product", "type": "VARCHAR", "description": "Product name (iPhone, iPad, Mac, etc.)"},
                        {"name": "region", "type": "VARCHAR", "description": "Geographic region"},
                        {"name": "revenue", "type": "DECIMAL", "description": "Revenue in USD"},
                        {"name": "units_sold", "type": "INTEGER", "description": "Number of units sold"},
                        {"name": "customer_segment", "type": "VARCHAR", "description": "Customer segment (consumer, enterprise, education)"}
                    ]
                },
                "apple_products_dim": {
                    "description": "Dimension table for product information",
                    "columns": [
                        {"name": "product_id", "type": "VARCHAR", "description": "Product identifier"},
                        {"name": "product_name", "type": "VARCHAR", "description": "Product name"},
                        {"name": "category", "type": "VARCHAR", "description": "Product category"},
                        {"name": "launch_date", "type": "DATE", "description": "Product launch date"}
                    ]
                },
                "apple_regions_dim": {
                    "description": "Dimension table for geographic regions",
                    "columns": [
                        {"name": "region_id", "type": "VARCHAR", "description": "Region identifier"},
                        {"name": "region_name", "type": "VARCHAR", "description": "Region name"},
                        {"name": "country", "type": "VARCHAR", "description": "Country name"},
                        {"name": "continent", "type": "VARCHAR", "description": "Continent"}
                    ]
                }
            }
        }
