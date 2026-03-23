"""
Result Formatter Service
Formats and enriches query results
"""

from typing import List, Dict, Any
from app.utils import get_logger

logger = get_logger(__name__)


class ResultFormatter:
    """
    Formats query results for presentation
    Provides data preview, statistics, and insights
    """
    
    @staticmethod
    def format_results(
        results: List[Dict[str, Any]],
        preview_rows: int = 5
    ) -> Dict[str, Any]:
        """
        Format query results with preview and statistics
        
        Args:
            results: Raw query results
            preview_rows: Number of rows to include in preview
        
        Returns:
            Formatted results with metadata
        """
        if not results:
            return {
                "data_preview": [],
                "full_data": [],
                "total_rows": 0,
                "columns": [],
                "statistics": {}
            }
        
        # Get column names
        columns = list(results[0].keys())
        
        # Create preview
        preview = results[:preview_rows]
        
        # Calculate statistics
        statistics = ResultFormatter._calculate_statistics(results, columns)
        
        return {
            "data_preview": preview,
            "full_data": results,          # ← all rows, no truncation
            "total_rows": len(results),
            "columns": columns,
            "statistics": statistics
        }
    
    @staticmethod
    def _calculate_statistics(
        results: List[Dict[str, Any]],
        columns: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate basic statistics for numeric columns
        
        Args:
            results: Query results
            columns: Column names
        
        Returns:
            Dictionary of statistics per column
        """
        stats = {}
        
        for col in columns:
            values = [row.get(col) for row in results if row.get(col) is not None]
            
            if not values:
                continue
            
            # Check if numeric
            if all(isinstance(v, (int, float)) for v in values):
                stats[col] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "sum": sum(values),
                    "count": len(values)
                }
            else:
                # For non-numeric, provide distinct count
                stats[col] = {
                    "distinct_count": len(set(str(v) for v in values)),
                    "count": len(values)
                }
        
        return stats
    
    @staticmethod
    def format_number(value: float, precision: int = 2) -> str:
        """
        Format number with thousands separator
        
        Args:
            value: Numeric value
            precision: Decimal places
        
        Returns:
            Formatted string
        """
        if value >= 1_000_000:
            return f"${value/1_000_000:.{precision}f}M"
        elif value >= 1_000:
            return f"${value/1_000:.{precision}f}K"
        else:
            return f"${value:.{precision}f}"
    
    @staticmethod
    def create_csv_export(results: List[Dict[str, Any]]) -> str:
        """
        Convert results to CSV format
        
        Args:
            results: Query results
        
        Returns:
            CSV string
        """
        if not results:
            return ""
        
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        
        return output.getvalue()
    
    @staticmethod
    def create_insights(
        results: List[Dict[str, Any]],
        statistics: Dict[str, Any]
    ) -> List[str]:
        """
        Generate insights from query results
        
        Args:
            results: Query results
            statistics: Statistical summary
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Total rows insight
        if len(results) > 0:
            insights.append(f"Query returned {len(results)} rows")
        
        # Revenue insights
        if 'revenue' in statistics:
            rev_stats = statistics['revenue']
            total_revenue = rev_stats.get('sum', 0)
            avg_revenue = rev_stats.get('avg', 0)
            
            insights.append(
                f"Total revenue: {ResultFormatter.format_number(total_revenue)}"
            )
            insights.append(
                f"Average revenue: {ResultFormatter.format_number(avg_revenue)}"
            )
        
        # Units insights
        if 'units_sold' in statistics:
            units_stats = statistics['units_sold']
            total_units = units_stats.get('sum', 0)
            
            insights.append(f"Total units sold: {total_units:,}")
        
        return insights
