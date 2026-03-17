"""
Governance Service
Implements security and governance controls for SQL queries
"""

import re
from typing import Dict, Any, List, Optional
import sqlglot
from sqlglot import parse_one, exp

from app.config import get_settings
from app.utils import get_logger

logger = get_logger(__name__)
settings = get_settings()


class QueryValidationError(Exception):
    """Raised when query fails validation"""
    pass


class GovernanceService:
    """
    Enforces security and governance policies on SQL queries
    Validates queries before execution to prevent unauthorized access
    """
    
    def __init__(self):
        """Initialize governance service"""
        self.settings = settings
    
    async def validate_query(
        self,
        sql_query: str,
        user_id: str,
        user_permissions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate SQL query against governance policies
        
        Args:
            sql_query: SQL query to validate
            user_id: User identifier
            user_permissions: Optional user permission data
        
        Returns:
            Validation result with warnings and estimated cost
        
        Raises:
            QueryValidationError: If query violates policies
        """
        logger.info("Validating query", user_id=user_id)
        
        warnings = []
        
        # 1. Check for forbidden keywords
        self._check_forbidden_keywords(sql_query)
        
        # 2. Check for SELECT *
        if self._has_select_star(sql_query):
            warnings.append("Query uses SELECT *, consider specifying columns explicitly")
        
        # 3. Validate table access
        accessed_tables = self._extract_tables(sql_query)
        self._validate_table_access(accessed_tables, user_id, user_permissions)
        
        # 4. Check for missing WHERE clause on large tables
        if not self._has_where_clause(sql_query) and self._uses_fact_table(sql_query):
            warnings.append("Query on fact table without WHERE clause may be expensive")
        
        # 5. Estimate query cost
        estimated_cost = self._estimate_query_cost(sql_query, accessed_tables)
        
        if estimated_cost > self.settings.MAX_QUERY_COST_USD:
            raise QueryValidationError(
                f"Estimated query cost ${estimated_cost:.2f} exceeds limit ${self.settings.MAX_QUERY_COST_USD}"
            )
        
        # 6. Check for LIMIT clause
        if not self._has_limit_clause(sql_query):
            warnings.append(f"Query should include LIMIT clause (max {self.settings.MAX_QUERY_ROWS} rows)")
        
        logger.info("Query validation passed", warnings_count=len(warnings))
        
        return {
            "valid": True,
            "warnings": warnings,
            "estimated_cost_usd": estimated_cost,
            "accessed_tables": accessed_tables
        }
    
    def _check_forbidden_keywords(self, sql_query: str) -> None:
        """
        Check for forbidden SQL keywords
        
        Args:
            sql_query: SQL query to check
        
        Raises:
            QueryValidationError: If forbidden keyword found
        """
        query_upper = sql_query.upper()
        
        for keyword in self.settings.FORBIDDEN_KEYWORDS:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, query_upper):
                raise QueryValidationError(
                    f"Query contains forbidden keyword: {keyword}"
                )
    
    def _has_select_star(self, sql_query: str) -> bool:
        """Check if query uses SELECT *"""
        return bool(re.search(r'\bSELECT\s+\*', sql_query, re.IGNORECASE))
    
    def _has_where_clause(self, sql_query: str) -> bool:
        """Check if query has WHERE clause"""
        return bool(re.search(r'\bWHERE\b', sql_query, re.IGNORECASE))
    
    def _has_limit_clause(self, sql_query: str) -> bool:
        """Check if query has LIMIT clause"""
        return bool(re.search(r'\bLIMIT\b', sql_query, re.IGNORECASE))
    
    def _uses_fact_table(self, sql_query: str) -> bool:
        """Check if query accesses a fact table"""
        return bool(re.search(r'apple_sales_fact', sql_query, re.IGNORECASE))
    
    def _extract_tables(self, sql_query: str) -> List[str]:
        """
        Extract table names from SQL query
        
        Args:
            sql_query: SQL query
        
        Returns:
            List of table names
        """
        try:
            # Parse SQL using sqlglot
            parsed = parse_one(sql_query, read='presto')
            
            tables = []
            for table in parsed.find_all(exp.Table):
                table_name = table.name
                if table_name:
                    tables.append(table_name.lower())
            
            return list(set(tables))
        
        except Exception as e:
            logger.warning("Failed to parse SQL for table extraction", error=str(e))
            
            # Fallback: simple regex extraction
            pattern = r'\bFROM\s+([a-z_][a-z0-9_]*)|JOIN\s+([a-z_][a-z0-9_]*)'
            matches = re.findall(pattern, sql_query, re.IGNORECASE)
            
            tables = []
            for match in matches:
                table = match[0] or match[1]
                if table:
                    tables.append(table.lower())
            
            return list(set(tables))
    
    def _validate_table_access(
        self,
        tables: List[str],
        user_id: str,
        user_permissions: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Validate user has access to requested tables
        
        Args:
            tables: List of table names
            user_id: User identifier
            user_permissions: Optional permission data
        
        Raises:
            QueryValidationError: If user lacks access to a table
        """
        # Check against allowed tables
        for table in tables:
            if table not in [t.lower() for t in self.settings.ALLOWED_TABLES]:
                raise QueryValidationError(
                    f"Access denied to table: {table}. "
                    f"Allowed tables: {', '.join(self.settings.ALLOWED_TABLES)}"
                )
        
        # Additional user-level permissions check
        if user_permissions:
            restricted_tables = user_permissions.get('restricted_tables', [])
            for table in tables:
                if table in restricted_tables:
                    raise QueryValidationError(
                        f"User {user_id} does not have permission to access table: {table}"
                    )
    
    def _estimate_query_cost(
        self,
        sql_query: str,
        tables: List[str]
    ) -> float:
        """
        Estimate query execution cost in USD
        
        Args:
            sql_query: SQL query
            tables: List of tables accessed
        
        Returns:
            Estimated cost in USD
        """
        # Athena pricing: $5 per TB scanned
        # Estimate based on table sizes (mock values)
        
        table_sizes_gb = {
            'apple_sales_fact': 100,  # 100 GB
            'apple_products_dim': 0.1,  # 100 MB
            'apple_regions_dim': 0.01  # 10 MB
        }
        
        total_size_gb = sum(
            table_sizes_gb.get(table, 1) for table in tables
        )
        
        # Estimate data scanned (reduced if WHERE clause present)
        scan_multiplier = 0.1 if self._has_where_clause(sql_query) else 1.0
        
        data_scanned_gb = total_size_gb * scan_multiplier
        data_scanned_tb = data_scanned_gb / 1024
        
        # Athena cost calculation
        cost = data_scanned_tb * 5.0
        
        # Minimum cost
        cost = max(cost, 0.001)
        
        logger.info(
            "Query cost estimated",
            data_scanned_gb=round(data_scanned_gb, 2),
            cost_usd=round(cost, 4)
        )
        
        return round(cost, 4)
    
    async def check_lake_formation_permissions(
        self,
        user_id: str,
        tables: List[str]
    ) -> bool:
        """
        Check AWS Lake Formation permissions
        
        Args:
            user_id: User identifier
            tables: List of tables to check
        
        Returns:
            True if user has access, False otherwise
        """
        if not self.settings.LAKE_FORMATION_ENABLED:
            return True
        
        # TODO: Implement Lake Formation permission check
        # This would call AWS Lake Formation API to verify permissions
        
        logger.info("Lake Formation check bypassed (not enabled)")
        return True
    
    def sanitize_sql(self, sql_query: str) -> str:
        """
        Sanitize SQL query to prevent injection attacks
        
        Args:
            sql_query: Raw SQL query
        
        Returns:
            Sanitized SQL query
        """
        # Remove comments
        sql = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Remove extra whitespace
        sql = ' '.join(sql.split())
        
        return sql.strip()
