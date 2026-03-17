"""
Time Resolution Utility
Converts natural language time references to SQL-compatible dates
"""

from datetime import datetime, timedelta
from typing import Tuple, Optional
import re
from dateutil.relativedelta import relativedelta


class TimeResolver:
    """
    Resolves natural language time expressions to date ranges
    """
    
    @staticmethod
    def resolve_time_expression(expression: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Convert natural language time expression to date range
        
        Args:
            expression: Time expression (e.g., "last quarter", "this year", "last 30 days")
        
        Returns:
            Tuple of (start_date, end_date) or (None, None) if not recognized
        
        Examples:
            "last quarter" -> (2024-10-01, 2024-12-31)
            "this year" -> (2024-01-01, 2024-12-31)
            "last 30 days" -> (2024-02-15, 2024-03-16)
        """
        expression = expression.lower().strip()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Last N days
        if match := re.search(r'last (\d+) days?', expression):
            days = int(match.group(1))
            start_date = today - timedelta(days=days)
            return start_date, today
        
        # Last N weeks
        if match := re.search(r'last (\d+) weeks?', expression):
            weeks = int(match.group(1))
            start_date = today - timedelta(weeks=weeks)
            return start_date, today
        
        # Last N months
        if match := re.search(r'last (\d+) months?', expression):
            months = int(match.group(1))
            start_date = today - relativedelta(months=months)
            return start_date, today
        
        # Last quarter
        if 'last quarter' in expression:
            current_quarter = (today.month - 1) // 3
            if current_quarter == 0:
                # Q4 of last year
                start_date = datetime(today.year - 1, 10, 1)
                end_date = datetime(today.year - 1, 12, 31)
            else:
                quarter_start_month = (current_quarter - 1) * 3 + 1
                start_date = datetime(today.year, quarter_start_month, 1)
                end_date = datetime(today.year, quarter_start_month + 2, 1) + relativedelta(months=1) - timedelta(days=1)
            return start_date, end_date
        
        # This quarter
        if 'this quarter' in expression or 'current quarter' in expression:
            current_quarter = (today.month - 1) // 3
            quarter_start_month = current_quarter * 3 + 1
            start_date = datetime(today.year, quarter_start_month, 1)
            end_date = datetime(today.year, quarter_start_month + 2, 1) + relativedelta(months=1) - timedelta(days=1)
            return start_date, end_date
        
        # Last year
        if 'last year' in expression:
            start_date = datetime(today.year - 1, 1, 1)
            end_date = datetime(today.year - 1, 12, 31)
            return start_date, end_date
        
        # This year
        if 'this year' in expression or 'current year' in expression:
            start_date = datetime(today.year, 1, 1)
            end_date = datetime(today.year, 12, 31)
            return start_date, end_date
        
        # This month
        if 'this month' in expression or 'current month' in expression:
            start_date = datetime(today.year, today.month, 1)
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)
            return start_date, end_date
        
        # Last month
        if 'last month' in expression:
            last_month = today.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1)
            end_date = last_month
            return start_date, end_date
        
        # Yesterday
        if 'yesterday' in expression:
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday
        
        # Today
        if 'today' in expression:
            return today, today
        
        # Specific year (e.g., "2023")
        if match := re.search(r'\b(20\d{2})\b', expression):
            year = int(match.group(1))
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            return start_date, end_date
        
        return None, None
    
    @staticmethod
    def format_date_for_sql(date: Optional[datetime]) -> Optional[str]:
        """
        Format datetime object to SQL-compatible string
        
        Args:
            date: Datetime object
        
        Returns:
            Date string in YYYY-MM-DD format
        """
        if date is None:
            return None
        return date.strftime('%Y-%m-%d')
    
    @staticmethod
    def extract_time_parameters(query: str) -> dict:
        """
        Extract time-related parameters from natural language query
        
        Args:
            query: Natural language query
        
        Returns:
            Dictionary with start_date and end_date
        """
        time_patterns = [
            r'last \d+ (?:day|week|month)s?',
            r'last (?:quarter|year|month)',
            r'this (?:quarter|year|month)',
            r'current (?:quarter|year|month)',
            r'yesterday',
            r'today',
            r'in \d{4}',
            r'\b20\d{2}\b'
        ]
        
        for pattern in time_patterns:
            if match := re.search(pattern, query, re.IGNORECASE):
                expression = match.group(0)
                start_date, end_date = TimeResolver.resolve_time_expression(expression)
                if start_date and end_date:
                    return {
                        'start_date': TimeResolver.format_date_for_sql(start_date),
                        'end_date': TimeResolver.format_date_for_sql(end_date),
                        'time_expression': expression
                    }
        
        return {}
