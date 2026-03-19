"""
Query Executor Service
Executes SQL queries on Amazon Athena or mock data
"""

import time
import uuid
import asyncio
import re
from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError
import pandas as pd

from app.config import get_settings
from app.utils import get_logger

logger = get_logger(__name__)
settings = get_settings()


class QueryExecutor:
    """
    Executes SQL queries on Amazon Athena
    Provides query monitoring and result retrieval
    """
    
    def __init__(self):
        """Initialize Athena client"""
        self.settings = settings
        
        if not self.settings.MOCK_MODE:
            # Build client config
            client_config = {'region_name': self.settings.AWS_REGION}
            
            # Add credentials if provided in .env
            if self.settings.AWS_ACCESS_KEY_ID and self.settings.AWS_SECRET_ACCESS_KEY:
                client_config['aws_access_key_id'] = self.settings.AWS_ACCESS_KEY_ID
                client_config['aws_secret_access_key'] = self.settings.AWS_SECRET_ACCESS_KEY
                # Add session token if provided (for temporary/MFA credentials)
                if self.settings.AWS_SESSION_TOKEN:
                    client_config['aws_session_token'] = self.settings.AWS_SESSION_TOKEN
                logger.info("Using credentials from environment variables")
            else:
                logger.info("Using AWS CLI credentials (default credential chain)")
            
            self.client = boto3.client('athena', **client_config)
        else:
            self.client = None
            logger.info("Query Executor running in MOCK mode")
            self._load_mock_data()
    
    def _load_mock_data(self):
        """Load mock data for testing"""
        try:
            self.mock_df = pd.read_csv(self.settings.MOCK_DATA_PATH)
            logger.info("Mock data loaded", rows=len(self.mock_df))
        except FileNotFoundError:
            # Create sample mock data if file doesn't exist
            self.mock_df = self._create_sample_data()
            logger.info("Using generated sample data", rows=len(self.mock_df))
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample data for testing"""
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Generate sample sales data
        products = ['iPhone', 'iPad', 'Mac', 'Apple Watch', 'AirPods']
        regions = ['North America', 'Europe', 'Asia Pacific', 'India', 'China', 'Japan']
        
        data = []
        start_date = datetime(2024, 1, 1)
        
        for i in range(1000):
            date = start_date + timedelta(days=i % 365)
            product = products[i % len(products)]
            region = regions[i % len(regions)]
            revenue = round(10000 + (i * 123.45) % 50000, 2)
            units = int(100 + (i * 7) % 500)
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'product': product,
                'region': region,
                'revenue': revenue,
                'units_sold': units,
                'customer_segment': ['consumer', 'enterprise', 'education'][i % 3]
            })
        
        return pd.DataFrame(data)
    
    async def execute_query(
        self,
        sql_query: str,
        query_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute SQL query on Athena
        
        Args:
            sql_query: SQL query to execute
            query_id: Optional query identifier
        
        Returns:
            Dictionary containing results and execution metadata
        """
        query_id = query_id or f"q_{uuid.uuid4().hex[:12]}"
        
        logger.info("Executing query", query_id=query_id, query=sql_query[:100])
        
        start_time = time.time()
        
        if self.settings.MOCK_MODE:
            results = await self._execute_mock_query(sql_query)
        else:
            results = await self._execute_athena_query(sql_query)
        
        execution_time = time.time() - start_time
        
        return {
            "query_id": query_id,
            "results": results,
            "execution_time_seconds": round(execution_time, 3),
            "row_count": len(results),
            "status": "completed"
        }
    
    async def _execute_athena_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute query on Amazon Athena
        
        Args:
            sql_query: SQL query to execute
        
        Returns:
            Query results as list of dictionaries
        """
        try:
            # Start query execution
            print(self.settings.ATHENA_DATABASE)
            print(self.settings.ATHENA_OUTPUT_LOCATION)
            print(sql_query)
            response = self.client.start_query_execution(
                QueryString=sql_query,
                QueryExecutionContext={
                    'Database': self.settings.ATHENA_DATABASE
                },
                ResultConfiguration={
                    'OutputLocation': self.settings.ATHENA_OUTPUT_LOCATION
                },
                # WorkGroup=self.settings.ATHENA_WORKGROUP
            )
            
            execution_id = response['QueryExecutionId']
            logger.info("Athena query started", execution_id=execution_id)
            
            # Wait for query to complete
            status = await self._wait_for_query_completion(execution_id)
            
            if status != 'SUCCEEDED':
                raise Exception(f"Query failed with status: {status}")
            
            # Get query results
            results = await self._get_query_results(execution_id)
            
            return results
        
        except ClientError as e:
            logger.error("Athena query failed", error=str(e))
            raise
    
    async def _wait_for_query_completion(
        self,
        execution_id: str,
        max_wait_seconds: int = None
    ) -> str:
        """
        Wait for Athena query to complete
        
        Args:
            execution_id: Athena query execution ID
            max_wait_seconds: Maximum time to wait
        
        Returns:
            Final query status
        """
        max_wait_seconds = max_wait_seconds or self.settings.ATHENA_QUERY_TIMEOUT
        start_time = time.time()
        
        while True:
            response = self.client.get_query_execution(
                QueryExecutionId=execution_id
            )
            
            status = response['QueryExecution']['Status']['State']
            
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                # Log execution stats
                if status == 'SUCCEEDED':
                    stats = response['QueryExecution'].get('Statistics', {})
                    data_scanned = stats.get('DataScannedInBytes', 0) / (1024 * 1024)  # MB
                    execution_time = stats.get('EngineExecutionTimeInMillis', 0) / 1000  # seconds
                    logger.info(
                        "Query completed",
                        execution_id=execution_id,
                        data_scanned_mb=round(data_scanned, 2),
                        execution_time_sec=round(execution_time, 2)
                    )
                elif status == 'FAILED':
                    reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                    logger.error("Query failed", execution_id=execution_id, reason=reason)
                
                return status
            
            if time.time() - start_time > max_wait_seconds:
                logger.warning("Query timeout exceeded", execution_id=execution_id)
                # Try to cancel the query
                try:
                    self.client.stop_query_execution(QueryExecutionId=execution_id)
                except Exception as e:
                    logger.error("Failed to stop query", error=str(e))
                return 'TIMEOUT'
            
            await asyncio.sleep(1)  # Use asyncio.sleep for async function
    
    async def _get_query_results(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve results from completed Athena query
        
        Args:
            execution_id: Athena query execution ID
        
        Returns:
            Query results as list of dictionaries
        """
        results = []
        next_token = None
        
        while True:
            kwargs = {'QueryExecutionId': execution_id}
            if next_token:
                kwargs['NextToken'] = next_token
            
            response = self.client.get_query_results(**kwargs)
            
            # First row contains column names
            if not results and response['ResultSet']['Rows']:
                column_names = [
                    col['VarCharValue']
                    for col in response['ResultSet']['Rows'][0]['Data']
                ]
                rows = response['ResultSet']['Rows'][1:]  # Skip header
            else:
                rows = response['ResultSet']['Rows']
            
            # Convert rows to dictionaries
            for row in rows:
                row_dict = {}
                for i, col in enumerate(row['Data']):
                    value = col.get('VarCharValue')
                    # Try to convert to appropriate type
                    if value is not None:
                        try:
                            # Try integer
                            if '.' not in value:
                                value = int(value)
                            else:
                                # Try float
                                value = float(value)
                        except ValueError:
                            pass  # Keep as string
                    
                    row_dict[column_names[i]] = value
                
                results.append(row_dict)
            
            # Check for more results
            next_token = response.get('NextToken')
            if not next_token:
                break
        
        logger.info("Query results retrieved", row_count=len(results))
        return results
    
    async def _execute_mock_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute query on mock data using pandas
        
        Args:
            sql_query: SQL query to execute
        
        Returns:
            Query results as list of dictionaries
        """
        try:
            logger.info("Executing mock query")
            
            # Simple SQL parsing for common patterns
            query_lower = sql_query.lower()
            
            df = self.mock_df.copy()
            
            # Parse WHERE clauses (simplified)
            if 'where' in query_lower:
                df = self._apply_where_clause(df, sql_query)
            
            # Parse GROUP BY (with aggregations)
            if 'group by' in query_lower:
                df = self._apply_group_by(df, sql_query)
            elif 'sum(' in query_lower or 'count(' in query_lower or 'avg(' in query_lower:
                # Aggregation without GROUP BY
                df = self._apply_aggregation(df, sql_query)
            
            # Parse ORDER BY
            if 'order by' in query_lower:
                df = self._apply_order_by(df, sql_query)
            
            # Parse LIMIT
            if 'limit' in query_lower:
                limit = self._extract_limit(sql_query)
                df = df.head(limit)
            else:
                df = df.head(100)  # Default limit
            
            # Convert to list of dictionaries
            results = df.to_dict('records')
            
            logger.info("Mock query executed", row_count=len(results))
            return results
        
        except Exception as e:
            logger.error("Mock query execution failed", error=str(e))
            # Return sample results on error
            return self.mock_df.head(5).to_dict('records')
    
    def _apply_where_clause(self, df: pd.DataFrame, sql_query: str) -> pd.DataFrame:
        """Apply WHERE clause filters to dataframe"""
        query_lower = sql_query.lower()
        
        # Extract product filter
        if "product = 'iphone'" in query_lower:
            df = df[df['product'] == 'iPhone']
        
        # Extract region filter
        if "region = 'india'" in query_lower:
            df = df[df['region'] == 'India']
        
        # Extract date filters
        import re
        date_pattern = r"date\s+between\s+'(\d{4}-\d{2}-\d{2})'\s+and\s+'(\d{4}-\d{2}-\d{2})'"
        if match := re.search(date_pattern, query_lower):
            start_date = match.group(1)
            end_date = match.group(2)
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        return df
    
    def _apply_aggregation(self, df: pd.DataFrame, sql_query: str) -> pd.DataFrame:
        """Apply aggregation functions"""
        query_lower = sql_query.lower()
        
        agg_dict = {}
        
        if 'sum(revenue)' in query_lower:
            agg_dict['revenue'] = 'sum'
        if 'sum(units_sold)' in query_lower:
            agg_dict['units_sold'] = 'sum'
        if 'count(*)' in query_lower:
            agg_dict['count'] = 'count'
        
        if agg_dict and 'group by' not in query_lower:
            # Simple aggregation without grouping
            result = {}
            if 'revenue' in agg_dict:
                result['total_revenue'] = df['revenue'].sum()
            if 'units_sold' in agg_dict:
                result['total_units'] = df['units_sold'].sum()
            
            return pd.DataFrame([result])
        
        return df
    
    def _apply_group_by(self, df: pd.DataFrame, sql_query: str) -> pd.DataFrame:
        """Apply GROUP BY clause"""
        import re
        
        # Extract GROUP BY columns
        group_by_pattern = r'group\s+by\s+([a-z_, ]+)'
        if match := re.search(group_by_pattern, sql_query.lower()):
            group_cols = [col.strip() for col in match.group(1).split(',')]
            
            # Define aggregations
            agg_dict = {}
            if 'sum(revenue)' in sql_query.lower():
                agg_dict['revenue'] = 'sum'
            if 'sum(units_sold)' in sql_query.lower():
                agg_dict['units_sold'] = 'sum'
            
            if agg_dict:
                df = df.groupby(group_cols, as_index=False).agg(agg_dict)
        
        return df
    
    def _apply_order_by(self, df: pd.DataFrame, sql_query: str) -> pd.DataFrame:
        """Apply ORDER BY clause"""
        import re
        
        order_pattern = r'order\s+by\s+([a-z_]+)(?:\s+(asc|desc))?'
        if match := re.search(order_pattern, sql_query.lower()):
            column = match.group(1)
            direction = match.group(2) or 'asc'
            
            if column in df.columns:
                ascending = direction == 'asc'
                df = df.sort_values(by=column, ascending=ascending)
        
        return df
    
    def _extract_limit(self, sql_query: str) -> int:
        """Extract LIMIT value from query"""
        import re
        
        limit_pattern = r'limit\s+(\d+)'
        if match := re.search(limit_pattern, sql_query.lower()):
            return int(match.group(1))
        
        return 1000  # Default limit
