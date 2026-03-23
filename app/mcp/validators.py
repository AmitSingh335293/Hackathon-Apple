"""
MCP Server Validators & SQL Helpers
Validation functions, constants, and SQL literal helpers used by MCP tools.
"""

import json
import re
from datetime import datetime
from typing import Any


# ── Constants ──────────────────────────────────────────────────────────────
VALID_CATEGORIES = [
    "Laptop", "Audio", "Tablet", "Smartphone", "Wearable",
    "Streaming Device", "Desktop", "Subscription Service", "Smart Speaker", "Accessories",
]
VALID_COUNTRIES = [
    "Australia", "Austria", "Canada", "China", "Colombia", "France", "Germany",
    "Italy", "Japan", "Mexico", "Netherlands", "Singapore", "South Korea", "Spain",
    "Taiwan", "Thailand", "UAE", "United Kingdom", "United States",
]
VALID_REPAIR_STATUSES = ["Completed", "Pending", "In Progress", "Rejected"]
VALID_TABLE_NAMES = {"sales", "products", "stores", "category", "warranty"}
VALID_ALIASES = {"s", "p", "st", "c", "w"}


# ── Validation helpers ─────────────────────────────────────────────────────
def _date(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"'{name}' must be YYYY-MM-DD, got {type(value).__name__}")
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise ValueError(f"'{name}' must be YYYY-MM-DD. Got: '{value}'")


def _pos_int(value: Any, name: str, default: int = None) -> int:
    if value is None and default is not None:
        return default
    try:
        v = int(value)
        if v <= 0:
            raise ValueError()
        return v
    except (ValueError, TypeError):
        raise ValueError(f"'{name}' must be a positive integer. Got: '{value}'")


def _enum(value: str, allowed: list, name: str) -> str:
    if value not in allowed:
        raise ValueError(f"'{name}' must be one of {allowed}. Got: '{value}'")
    return value


def _s(value: str) -> str:
    """Escape string for safe SQL literal embedding."""
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")
    return value.replace("'", "''").replace(";", "").replace("--", "")


def _lit(value) -> str:
    """Convert validated Python value to a SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return f"'{_s(str(value))}'"


# ── Response helpers ───────────────────────────────────────────────────────
def _ok(sql: str, extra: dict = None) -> str:
    result = {"status": "success", "sql": sql}
    if extra:
        result.update(extra)
    return json.dumps(result, indent=2)


def _err(errors: list) -> str:
    return json.dumps({"status": "error", "errors": errors}, indent=2)


# ── SQL safety validation ─────────────────────────────────────────────────
def _validate_sql_safety(sql: str) -> list:
    issues = []
    upper = sql.upper().strip()
    if not upper.startswith("SELECT"):
        issues.append("Query must start with SELECT. Only read operations are allowed.")
    for kw in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "EXEC", "EXECUTE", "CREATE", "GRANT", "REVOKE"]:
        if re.search(rf"\b{kw}\b", upper):
            issues.append(f"Blocked: dangerous keyword '{kw}' detected. Only SELECT is allowed.")
    for groups in re.findall(r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)", upper):
        for ref in groups:
            if ref and ref.lower() not in VALID_TABLE_NAMES and ref.lower() not in VALID_ALIASES:
                issues.append(f"Unknown table '{ref}'. Valid tables: {sorted(VALID_TABLE_NAMES)}")
    return issues
