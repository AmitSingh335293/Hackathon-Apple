"""
Apple Retail Sales MCP Server
16 tools (Q01-Q15 + generate_sql). Each tool inlines its SQL directly,
substituting validated parameters in-place.
"""

import json
import logging
import os
from typing import Optional, Annotated

from fastmcp import FastMCP

from app.mcp.validators import (
    VALID_CATEGORIES, VALID_COUNTRIES, VALID_REPAIR_STATUSES,
    _date, _pos_int, _enum, _s, _lit, _ok, _err, _validate_sql_safety,
)

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "apple-retail-sql",
    instructions=(
        "You are a SQL query assistant for Apple Retail Sales data. "
        "Use the predefined tools (Q01-Q15) for common business queries. "
        "Only use generate_sql when no predefined tool fits the request."
    ),
)


# ── Q01: Total Sales Revenue by Country ───────────────────────────────────
@mcp.tool(
    name="total_sales_revenue_by_country",
    description=(
        "Returns total revenue (quantity x price), total units sold, and transaction count per country "
        "for a given date range. Used by regional finance teams to compare country-level sales "
        "performance across custom periods such as monthly, quarterly, or year-to-date."
    ),
    tags={"sales", "revenue", "country", "finance", "reporting"},
)
def total_sales_revenue_by_country(
    start_date: Annotated[str, "Start date of reporting period (YYYY-MM-DD). Example: 2023-01-01"],
    end_date: Annotated[str, "End date of reporting period (YYYY-MM-DD). Example: 2023-12-31"],
) -> str:
    """[Q01] Total Sales Revenue by Country for a Given Date Range."""
    errors = []
    try:
        sd = _date(start_date, "start_date")
    except ValueError as e:
        errors.append(str(e)); sd = None
    try:
        ed = _date(end_date, "end_date")
    except ValueError as e:
        errors.append(str(e)); ed = None
    if errors:
        return _err(errors)
    sql = (
        f"SELECT st.Country, COUNT(s.sale_id) AS total_transactions, "
        f"SUM(s.quantity) AS total_units_sold, SUM(s.quantity * p.Price) AS total_revenue "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN stores st ON s.store_id = st.Store_ID "
        f"WHERE date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)} "
        f"GROUP BY st.Country ORDER BY total_revenue DESC"
    )
    return _ok(sql, {"query_id": "Q01", "output_columns": ["Country", "total_transactions", "total_units_sold", "total_revenue"]})


# ── Q02: Top N Best-Selling Products ──────────────────────────────────────
@mcp.tool(
    name="top_products_by_category",
    description=(
        "Returns the top N products ranked by units sold, optionally filtered by product category "
        "and/or date range. When no category is specified, returns overall top sellers across all "
        "categories. Used by product managers to identify best sellers globally or per category."
    ),
    tags={"sales", "products", "category", "ranking", "best-sellers", "top"},
)
def top_products_by_category(
    category_name: Annotated[Optional[str], "Product category (optional, default: all). Allowed: Laptop, Audio, Tablet, Smartphone, Wearable, Streaming Device, Desktop, Subscription Service, Smart Speaker, Accessories"] = None,
    start_date: Annotated[Optional[str], "Start date (YYYY-MM-DD, optional, default: all time). Example: 2023-01-01"] = None,
    end_date: Annotated[Optional[str], "End date (YYYY-MM-DD, optional, default: all time). Example: 2023-12-31"] = None,
    top_n: Annotated[Optional[int], "Number of top products to return (default: 10). Example: 5"] = None,
) -> str:
    """[Q02] Top N Best-Selling Products, optionally filtered by Category and Time Period."""
    errors = []
    cat_filter = "1=1"
    if category_name:
        try:
            cat = _enum(category_name, VALID_CATEGORIES, "category_name")
            cat_filter = f"c.category_name = {_lit(cat)}"
        except ValueError as e:
            errors.append(str(e))
    sd = "2019-01-01"; ed = "2026-12-31"
    if start_date:
        try:
            sd = _date(start_date, "start_date")
        except ValueError as e:
            errors.append(str(e))
    if end_date:
        try:
            ed = _date(end_date, "end_date")
        except ValueError as e:
            errors.append(str(e))
    n = _pos_int(top_n, "top_n", default=10)
    if errors:
        return _err(errors)
    sql = (
        f"SELECT p.Product_Name, c.category_name, SUM(s.quantity) AS total_units_sold, "
        f"SUM(s.quantity * p.Price) AS total_revenue, COUNT(s.sale_id) AS transaction_count "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN category c ON p.Category_ID = c.category_id "
        f"WHERE {cat_filter} "
        f"AND date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)} "
        f"GROUP BY p.Product_Name, c.category_name ORDER BY total_units_sold DESC LIMIT {n}"
    )
    return _ok(sql, {"query_id": "Q02", "output_columns": ["Product_Name", "category_name", "total_units_sold", "total_revenue", "transaction_count"]})


# ── Q03: Store-Level Sales Performance by Country ─────────────────────────
@mcp.tool(
    name="store_performance_by_country",
    description=(
        "Returns per-store sales metrics (revenue, units, average order quantity, transaction count) "
        "for all stores in a given country within a date range. Used by retail operations teams "
        "for head-to-head store comparison within a country."
    ),
    tags={"sales", "stores", "country", "performance", "operations"},
)
def store_performance_by_country(
    country: Annotated[str, "Country to filter. Allowed: Australia, Austria, Canada, China, Colombia, France, Germany, Italy, Japan, Mexico, Netherlands, Singapore, South Korea, Spain, Taiwan, Thailand, UAE, United Kingdom, United States"],
    start_date: Annotated[Optional[str], "Start date (YYYY-MM-DD, default: all time). Example: 2023-01-01"] = None,
    end_date: Annotated[Optional[str], "End date (YYYY-MM-DD, default: all time). Example: 2023-12-31"] = None,
) -> str:
    """[Q03] Store-Level Sales Performance Comparison for a Country."""
    errors = []
    try:
        co = _enum(country, VALID_COUNTRIES, "country")
    except ValueError as e:
        errors.append(str(e)); co = None
    sd = "2019-01-01"; ed = "2026-12-31"
    if start_date:
        try:
            sd = _date(start_date, "start_date")
        except ValueError as e:
            errors.append(str(e))
    if end_date:
        try:
            ed = _date(end_date, "end_date")
        except ValueError as e:
            errors.append(str(e))
    if errors:
        return _err(errors)
    sql = (
        f"SELECT st.Store_ID, st.Store_Name, st.City, COUNT(s.sale_id) AS total_transactions, "
        f"SUM(s.quantity) AS total_units_sold, ROUND(AVG(s.quantity), 2) AS avg_order_quantity, "
        f"SUM(s.quantity * p.Price) AS total_revenue, "
        f"ROUND(SUM(s.quantity * p.Price) / COUNT(s.sale_id), 2) AS avg_revenue_per_transaction "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN stores st ON s.store_id = st.Store_ID "
        f"WHERE st.Country = {_lit(co)} "
        f"AND date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)} "
        f"GROUP BY st.Store_ID, st.Store_Name, st.City ORDER BY total_revenue DESC"
    )
    return _ok(sql, {"query_id": "Q03", "output_columns": ["Store_ID", "Store_Name", "City", "total_transactions", "total_units_sold", "avg_order_quantity", "total_revenue", "avg_revenue_per_transaction"]})


# ── Q04: Monthly Sales Trend for a Product ────────────────────────────────
@mcp.tool(
    name="monthly_sales_trend_by_product",
    description=(
        "Returns month-over-month sales trend (units and revenue) for a specific product. "
        "Useful for tracking product lifecycle, seasonality, and post-launch trajectory. "
        "Used by product marketing managers to monitor individual product performance over time."
    ),
    tags={"sales", "products", "trend", "monthly", "marketing"},
)
def monthly_sales_trend_by_product(
    product_name: Annotated[str, "Exact name of the product. Example: iPhone 15"],
    start_date: Annotated[Optional[str], "Start date (YYYY-MM-DD, default: all time). Example: 2022-01-01"] = None,
    end_date: Annotated[Optional[str], "End date (YYYY-MM-DD, default: all time). Example: 2024-12-31"] = None,
) -> str:
    """[Q04] Monthly Sales Trend for a Specific Product."""
    if not product_name or not product_name.strip():
        return _err(["'product_name' is required."])
    errors = []
    pn = _s(product_name.strip())
    sd = "2019-01-01"; ed = "2026-12-31"
    if start_date:
        try:
            sd = _date(start_date, "start_date")
        except ValueError as e:
            errors.append(str(e))
    if end_date:
        try:
            ed = _date(end_date, "end_date")
        except ValueError as e:
            errors.append(str(e))
    if errors:
        return _err(errors)
    sql = (
        f"SELECT date_format(date_parse(s.sale_date, '%d-%m-%Y'), '%Y-%m') AS sale_month, "
        f"p.Product_Name, SUM(s.quantity) AS total_units_sold, "
        f"SUM(s.quantity * p.Price) AS total_revenue, COUNT(s.sale_id) AS transaction_count "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"WHERE p.Product_Name = '{pn}' "
        f"AND date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)} "
        f"GROUP BY date_format(date_parse(s.sale_date, '%d-%m-%Y'), '%Y-%m'), p.Product_Name ORDER BY sale_month ASC"
    )
    return _ok(sql, {"query_id": "Q04", "output_columns": ["sale_month", "Product_Name", "total_units_sold", "total_revenue", "transaction_count"]})


# ── Q05: Warranty Claim Rate by Category ──────────────────────────────────
@mcp.tool(
    name="warranty_claim_rate_by_category",
    description=(
        "Returns warranty claim counts and claim rate (claims / total sales) grouped by product "
        "category, optionally filtered by repair status. Used by QA teams to identify product "
        "quality issues per category and by service teams to monitor claim backlogs."
    ),
    tags={"warranty", "quality", "category", "claims", "service"},
)
def warranty_claim_rate_by_category(
    repair_status: Annotated[Optional[str], "Filter by repair status: Completed, Pending, In Progress, Rejected. Default: all."] = None,
) -> str:
    """[Q05] Warranty Claim Rate by Product Category and Repair Status."""
    errors = []
    rs_filter = "1=1"
    if repair_status:
        try:
            rs = _enum(repair_status, VALID_REPAIR_STATUSES, "repair_status")
            rs_filter = f"w.repair_status = {_lit(rs)}"
        except ValueError as e:
            errors.append(str(e))
    if errors:
        return _err(errors)
    sql = (
        f"SELECT c.category_name, w.repair_status, COUNT(w.claim_id) AS total_claims, "
        f"total_sales.category_sales, "
        f"ROUND(COUNT(w.claim_id) * 100.0 / total_sales.category_sales, 4) AS claim_rate_pct "
        f"FROM warranty w JOIN sales s ON w.sale_id = s.sale_id "
        f"JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN category c ON p.Category_ID = c.category_id "
        f"JOIN (SELECT c2.category_id, COUNT(s2.sale_id) AS category_sales "
        f"      FROM sales s2 JOIN products p2 ON s2.product_id = p2.Product_ID "
        f"      JOIN category c2 ON p2.Category_ID = c2.category_id GROUP BY c2.category_id) "
        f"total_sales ON c.category_id = total_sales.category_id "
        f"WHERE {rs_filter} "
        f"GROUP BY c.category_name, w.repair_status, total_sales.category_sales "
        f"ORDER BY claim_rate_pct DESC"
    )
    return _ok(sql, {"query_id": "Q05", "output_columns": ["category_name", "repair_status", "total_claims", "category_sales", "claim_rate_pct"]})


# ── Q06: Year-over-Year Sales Growth ──────────────────────────────────────
@mcp.tool(
    name="yoy_sales_growth",
    description=(
        "Compares total revenue between two specified years for a given country and/or category, "
        "computing absolute and percentage growth. Essential for annual business reviews and "
        "strategic planning. Supports filtering by country and product category."
    ),
    tags={"sales", "revenue", "growth", "yoy", "analytics", "finance"},
)
def yoy_sales_growth(
    year_current: Annotated[int, "The current/target year for comparison. Example: 2023"],
    year_previous: Annotated[int, "The previous/baseline year for comparison. Example: 2022"],
    country: Annotated[Optional[str], "Filter to a specific country (default: all). Example: United States"] = None,
    category_name: Annotated[Optional[str], "Filter to a specific category (default: all). Example: Laptop"] = None,
) -> str:
    """[Q06] Year-over-Year Sales Growth by Country and Category."""
    errors = []
    try:
        yc = _pos_int(year_current, "year_current")
    except ValueError as e:
        errors.append(str(e)); yc = None
    try:
        yp = _pos_int(year_previous, "year_previous")
    except ValueError as e:
        errors.append(str(e)); yp = None
    co_filter = "1=1"
    if country:
        try:
            co_filter = f"st.Country = {_lit(_enum(country, VALID_COUNTRIES, 'country'))}"
        except ValueError as e:
            errors.append(str(e))
    cat_filter = "1=1"
    if category_name:
        try:
            cat_filter = f"c.category_name = {_lit(_enum(category_name, VALID_CATEGORIES, 'category_name'))}"
        except ValueError as e:
            errors.append(str(e))
    if errors:
        return _err(errors)
    sql = (
        f"SELECT st.Country, c.category_name, "
        f"SUM(CASE WHEN year(date_parse(s.sale_date, '%d-%m-%Y')) = {yc} THEN s.quantity * p.Price ELSE 0 END) AS revenue_current_year, "
        f"SUM(CASE WHEN year(date_parse(s.sale_date, '%d-%m-%Y')) = {yp} THEN s.quantity * p.Price ELSE 0 END) AS revenue_previous_year, "
        f"SUM(CASE WHEN year(date_parse(s.sale_date, '%d-%m-%Y')) = {yc} THEN s.quantity * p.Price ELSE 0 END) - "
        f"SUM(CASE WHEN year(date_parse(s.sale_date, '%d-%m-%Y')) = {yp} THEN s.quantity * p.Price ELSE 0 END) AS revenue_growth, "
        f"ROUND((SUM(CASE WHEN year(date_parse(s.sale_date, '%d-%m-%Y')) = {yc} THEN s.quantity * p.Price ELSE 0 END) - "
        f"SUM(CASE WHEN year(date_parse(s.sale_date, '%d-%m-%Y')) = {yp} THEN s.quantity * p.Price ELSE 0 END)) * 100.0 / "
        f"NULLIF(SUM(CASE WHEN year(date_parse(s.sale_date, '%d-%m-%Y')) = {yp} THEN s.quantity * p.Price ELSE 0 END), 0), 2) AS growth_pct "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN stores st ON s.store_id = st.Store_ID "
        f"JOIN category c ON p.Category_ID = c.category_id "
        f"WHERE {co_filter} AND {cat_filter} "
        f"GROUP BY st.Country, c.category_name "
        f"HAVING revenue_current_year > 0 OR revenue_previous_year > 0 "
        f"ORDER BY growth_pct DESC"
    )
    return _ok(sql, {"query_id": "Q06", "output_columns": ["Country", "category_name", "revenue_current_year", "revenue_previous_year", "revenue_growth", "growth_pct"]})


# ── Q07: New Product Launch Performance ───────────────────────────────────
@mcp.tool(
    name="new_product_launch_performance",
    description=(
        "Returns all products launched after a specified date along with their cumulative "
        "sales performance (units, revenue, transaction count). Used by product strategy teams "
        "to evaluate new product launches and track post-launch trajectory."
    ),
    tags={"products", "launch", "performance", "strategy", "sales"},
)
def new_product_launch_performance(
    launch_date_after: Annotated[str, "Only include products launched on or after this date (YYYY-MM-DD). Example: 2023-01-01"],
    category_name: Annotated[Optional[str], "Filter to a specific category (default: all). Example: Smartphone"] = None,
) -> str:
    """[Q07] Products Launched After a Date with Sales Performance."""
    errors = []
    try:
        ld = _date(launch_date_after, "launch_date_after")
    except ValueError as e:
        errors.append(str(e)); ld = None
    cat_filter = "1=1"
    if category_name:
        try:
            cat_filter = f"c.category_name = {_lit(_enum(category_name, VALID_CATEGORIES, 'category_name'))}"
        except ValueError as e:
            errors.append(str(e))
    if errors:
        return _err(errors)
    sql = (
        f"SELECT p.Product_ID, p.Product_Name, c.category_name, p.Launch_Date, p.Price, "
        f"COALESCE(SUM(s.quantity), 0) AS total_units_sold, "
        f"COALESCE(SUM(s.quantity * p.Price), 0) AS total_revenue, "
        f"COUNT(s.sale_id) AS transaction_count "
        f"FROM products p JOIN category c ON p.Category_ID = c.category_id "
        f"LEFT JOIN sales s ON p.Product_ID = s.product_id "
        f"WHERE p.Launch_Date >= DATE {_lit(ld)} AND {cat_filter} "
        f"GROUP BY p.Product_ID, p.Product_Name, c.category_name, p.Launch_Date, p.Price "
        f"ORDER BY p.Launch_Date DESC"
    )
    return _ok(sql, {"query_id": "Q07", "output_columns": ["Product_ID", "Product_Name", "category_name", "Launch_Date", "Price", "total_units_sold", "total_revenue", "transaction_count"]})


# ── Q08: Warranty Claims by Location ──────────────────────────────────────
@mcp.tool(
    name="warranty_claims_by_location",
    description=(
        "Returns detailed warranty claims including product details, claim dates, and repair status "
        "for a given store, city, or country. Supports drill-down from high-level claim metrics to "
        "individual claim records. Used by service center managers to manage repair workloads."
    ),
    tags={"warranty", "claims", "location", "service", "store", "city"},
)
def warranty_claims_by_location(
    repair_status: Annotated[Optional[str], "Filter by status: Completed, Pending, In Progress, Rejected"] = None,
    country: Annotated[Optional[str], "Filter by country. Example: Japan"] = None,
    city: Annotated[Optional[str], "Filter by city. Example: Tokyo"] = None,
    store_name: Annotated[Optional[str], "Filter by exact store name. Example: Apple Fifth Avenue"] = None,
    limit: Annotated[Optional[int], "Maximum rows to return (default: 100). Example: 50"] = None,
) -> str:
    """[Q08] Warranty Claims Detail for a Specific Store, City, or Country."""
    errors = []
    conditions = []
    if repair_status:
        try:
            conditions.append(f"w.repair_status = {_lit(_enum(repair_status, VALID_REPAIR_STATUSES, 'repair_status'))}")
        except ValueError as e:
            errors.append(str(e))
    if country:
        conditions.append(f"st.Country = {_lit(country)}")
    if city:
        conditions.append(f"st.City = {_lit(city)}")
    if store_name:
        conditions.append(f"st.Store_Name = {_lit(store_name)}")
    lim = _pos_int(limit, "limit", default=100)
    if errors:
        return _err(errors)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = (
        f"SELECT w.claim_id, w.claim_date, w.repair_status, s.sale_id, s.sale_date, s.quantity, "
        f"p.Product_Name, c.category_name, p.Price, st.Store_Name, st.City, st.Country "
        f"FROM warranty w JOIN sales s ON w.sale_id = s.sale_id "
        f"JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN category c ON p.Category_ID = c.category_id "
        f"JOIN stores st ON s.store_id = st.Store_ID "
        f"{where} ORDER BY w.claim_date DESC LIMIT {lim}"
    )
    return _ok(sql, {"query_id": "Q08", "output_columns": ["claim_id", "claim_date", "repair_status", "sale_id", "sale_date", "quantity", "Product_Name", "category_name", "Price", "Store_Name", "City", "Country"]})


# ── Q09: Product Revenue Share in Category ────────────────────────────────
@mcp.tool(
    name="product_revenue_share_in_category",
    description=(
        "Calculates each product's revenue share (%) within its category for a given time period. "
        "Identifies dominant products vs underperformers within a category. Used by category managers "
        "to understand product-level market share and portfolio concentration."
    ),
    tags={"sales", "revenue", "products", "category", "market-share", "analytics"},
)
def product_revenue_share_in_category(
    category_name: Annotated[str, "Product category. Allowed: Laptop, Audio, Tablet, Smartphone, Wearable, Streaming Device, Desktop, Subscription Service, Smart Speaker, Accessories"],
    start_date: Annotated[str, "Start of analysis period (YYYY-MM-DD). Example: 2023-01-01"],
    end_date: Annotated[str, "End of analysis period (YYYY-MM-DD). Example: 2023-12-31"],
) -> str:
    """[Q09] Revenue Contribution by Product Within a Category (Market Share)."""
    errors = []
    try:
        cat = _enum(category_name, VALID_CATEGORIES, "category_name")
    except ValueError as e:
        errors.append(str(e)); cat = None
    try:
        sd = _date(start_date, "start_date")
    except ValueError as e:
        errors.append(str(e)); sd = None
    try:
        ed = _date(end_date, "end_date")
    except ValueError as e:
        errors.append(str(e)); ed = None
    if errors:
        return _err(errors)
    sql = (
        f"SELECT p.Product_Name, SUM(s.quantity * p.Price) AS product_revenue, "
        f"cat_total.category_revenue, "
        f"ROUND(SUM(s.quantity * p.Price) * 100.0 / cat_total.category_revenue, 2) AS revenue_share_pct "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN category c ON p.Category_ID = c.category_id "
        f"JOIN (SELECT c2.category_id, SUM(s2.quantity * p2.Price) AS category_revenue "
        f"      FROM sales s2 JOIN products p2 ON s2.product_id = p2.Product_ID "
        f"      JOIN category c2 ON p2.Category_ID = c2.category_id "
        f"      WHERE c2.category_name = {_lit(cat)} "
        f"      AND date_parse(s2.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)} "
        f"      GROUP BY c2.category_id) cat_total ON c.category_id = cat_total.category_id "
        f"WHERE c.category_name = {_lit(cat)} "
        f"AND date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)} "
        f"GROUP BY p.Product_Name, cat_total.category_revenue ORDER BY revenue_share_pct DESC"
    )
    return _ok(sql, {"query_id": "Q09", "output_columns": ["Product_Name", "product_revenue", "category_revenue", "revenue_share_pct"]})


# ── Q10: Quarterly Store Sales Summary ────────────────────────────────────
@mcp.tool(
    name="quarterly_store_sales_summary",
    description=(
        "Returns quarterly sales metrics per store with a running cumulative total across quarters "
        "for a given year. Enables tracking store trajectory and ranking over time within a year. "
        "Used by operations directors to review quarterly store scorecards."
    ),
    tags={"sales", "stores", "quarterly", "operations", "cumulative", "reporting"},
)
def quarterly_store_sales_summary(
    year: Annotated[int, "Year for the quarterly breakdown. Example: 2023"],
    country: Annotated[Optional[str], "Filter to stores in a specific country. Example: United States"] = None,
    store_name: Annotated[Optional[str], "Filter to a specific store. Example: Apple Fifth Avenue"] = None,
) -> str:
    """[Q10] Quarterly Sales Summary with Running Total by Store."""
    errors = []
    try:
        yr = _pos_int(year, "year")
    except ValueError as e:
        errors.append(str(e)); yr = None
    co_filter = "1=1"
    if country:
        try:
            co_filter = f"st.Country = {_lit(_enum(country, VALID_COUNTRIES, 'country'))}"
        except ValueError as e:
            errors.append(str(e))
    sn_filter = "1=1"
    if store_name:
        sn_filter = f"st.Store_Name = {_lit(store_name)}"
    if errors:
        return _err(errors)
    sql = (
        f"SELECT st.Store_Name, st.City, st.Country, "
        f"CONCAT(CAST(year(date_parse(s.sale_date, '%d-%m-%Y')) AS VARCHAR), '-Q', CAST(quarter(date_parse(s.sale_date, '%d-%m-%Y')) AS VARCHAR)) AS quarter, "
        f"SUM(s.quantity) AS quarterly_units, SUM(s.quantity * p.Price) AS quarterly_revenue, "
        f"SUM(SUM(s.quantity * p.Price)) OVER (PARTITION BY st.Store_ID ORDER BY "
        f"year(date_parse(s.sale_date, '%d-%m-%Y')), quarter(date_parse(s.sale_date, '%d-%m-%Y'))) AS cumulative_revenue "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN stores st ON s.store_id = st.Store_ID "
        f"WHERE year(date_parse(s.sale_date, '%d-%m-%Y')) = {yr} AND {co_filter} AND {sn_filter} "
        f"GROUP BY st.Store_ID, st.Store_Name, st.City, st.Country, "
        f"year(date_parse(s.sale_date, '%d-%m-%Y')), quarter(date_parse(s.sale_date, '%d-%m-%Y')) "
        f"ORDER BY st.Store_Name, quarter"
    )
    return _ok(sql, {"query_id": "Q10", "output_columns": ["Store_Name", "City", "Country", "quarter", "quarterly_units", "quarterly_revenue", "cumulative_revenue"]})


# ── Q11: Top Warranty Claim Products ─────────────────────────────────────
@mcp.tool(
    name="top_warranty_claim_products",
    description=(
        "Identifies products with the highest ratio of warranty claims to total sales within a date range. "
        "Supports filtering by category and a minimum sales threshold to exclude low-volume noise. "
        "Used by quality and compliance teams to pinpoint the most problematic products."
    ),
    tags={"warranty", "quality", "products", "compliance", "claims", "risk"},
)
def top_warranty_claim_products(
    start_date: Annotated[str, "Start of analysis period (YYYY-MM-DD). Example: 2022-01-01"],
    end_date: Annotated[str, "End of analysis period (YYYY-MM-DD). Example: 2024-12-31"],
    category_name: Annotated[Optional[str], "Filter to specific category (default: all). Example: Wearable"] = None,
    top_n: Annotated[Optional[int], "Number of top problematic products (default: 10). Example: 5"] = None,
    min_sales: Annotated[Optional[int], "Minimum sales for inclusion (default: 100). Example: 500"] = None,
) -> str:
    """[Q11] Products with Highest Warranty Claim Rate (Top N Problem Products)."""
    errors = []
    try:
        sd = _date(start_date, "start_date")
    except ValueError as e:
        errors.append(str(e)); sd = None
    try:
        ed = _date(end_date, "end_date")
    except ValueError as e:
        errors.append(str(e)); ed = None
    n = _pos_int(top_n, "top_n", default=10)
    ms = _pos_int(min_sales, "min_sales", default=100)
    cat_filter = "1=1"
    if category_name:
        try:
            cat_filter = f"c.category_name = {_lit(_enum(category_name, VALID_CATEGORIES, 'category_name'))}"
        except ValueError as e:
            errors.append(str(e))
    if errors:
        return _err(errors)
    sql = (
        f"SELECT p.Product_Name, c.category_name, COUNT(DISTINCT s.sale_id) AS total_sales, "
        f"COUNT(DISTINCT w.claim_id) AS total_claims, "
        f"ROUND(COUNT(DISTINCT w.claim_id) * 100.0 / NULLIF(COUNT(DISTINCT s.sale_id), 0), 4) AS claim_rate_pct "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN category c ON p.Category_ID = c.category_id "
        f"LEFT JOIN warranty w ON s.sale_id = w.sale_id "
        f"WHERE {cat_filter} "
        f"AND date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)} "
        f"GROUP BY p.Product_Name, c.category_name "
        f"HAVING COUNT(DISTINCT s.sale_id) > {ms} "
        f"ORDER BY claim_rate_pct DESC LIMIT {n}"
    )
    return _ok(sql, {"query_id": "Q11", "output_columns": ["Product_Name", "category_name", "total_sales", "total_claims", "claim_rate_pct"]})


# ── Q12: City Sales Ranking by Country ────────────────────────────────────
@mcp.tool(
    name="city_sales_ranking_by_country",
    description=(
        "Ranks all cities within a given country by total revenue and provides each city's share "
        "of the country's total revenue. Used by regional directors to identify dominant vs emerging "
        "city-level markets within a country for a given period."
    ),
    tags={"sales", "revenue", "city", "country", "ranking", "regional"},
)
def city_sales_ranking_by_country(
    country: Annotated[str, "Country to analyze. Allowed: Australia, Austria, Canada, China, Colombia, France, Germany, Italy, Japan, Mexico, Netherlands, Singapore, South Korea, Spain, Taiwan, Thailand, UAE, United Kingdom, United States"],
    start_date: Annotated[str, "Start date of analysis period (YYYY-MM-DD). Example: 2023-01-01"],
    end_date: Annotated[str, "End date of analysis period (YYYY-MM-DD). Example: 2023-12-31"],
) -> str:
    """[Q12] City-Level Sales Ranking Within a Country."""
    errors = []
    try:
        co = _enum(country, VALID_COUNTRIES, "country")
    except ValueError as e:
        errors.append(str(e)); co = None
    try:
        sd = _date(start_date, "start_date")
    except ValueError as e:
        errors.append(str(e)); sd = None
    try:
        ed = _date(end_date, "end_date")
    except ValueError as e:
        errors.append(str(e)); ed = None
    if errors:
        return _err(errors)
    sql = (
        f"SELECT st.City, COUNT(DISTINCT st.Store_ID) AS store_count, SUM(s.quantity) AS total_units, "
        f"SUM(s.quantity * p.Price) AS city_revenue, "
        f"SUM(SUM(s.quantity * p.Price)) OVER () AS country_total_revenue, "
        f"ROUND(SUM(s.quantity * p.Price) * 100.0 / SUM(SUM(s.quantity * p.Price)) OVER (), 2) AS revenue_share_pct, "
        f"RANK() OVER (ORDER BY SUM(s.quantity * p.Price) DESC) AS revenue_rank "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN stores st ON s.store_id = st.Store_ID "
        f"WHERE st.Country = {_lit(co)} "
        f"AND date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)} "
        f"GROUP BY st.City ORDER BY revenue_rank"
    )
    return _ok(sql, {"query_id": "Q12", "output_columns": ["City", "store_count", "total_units", "city_revenue", "country_total_revenue", "revenue_share_pct", "revenue_rank"]})


# ── Q13: Average Days to Warranty Claim ───────────────────────────────────
@mcp.tool(
    name="avg_days_to_warranty_claim",
    description=(
        "Calculates the average number of days between the original sale date and the warranty "
        "claim date per product. Identifies products that fail quickly vs those with delayed issues. "
        "Used by engineering and quality teams to understand mean-time-to-failure patterns."
    ),
    tags={"warranty", "quality", "engineering", "mean-time-to-failure", "products", "analytics"},
)
def avg_days_to_warranty_claim(
    category_name: Annotated[Optional[str], "Filter to specific product category. Example: Smartphone"] = None,
    repair_status: Annotated[Optional[str], "Filter to specific repair status: Completed, Pending, In Progress, Rejected"] = None,
    min_claims: Annotated[Optional[int], "Minimum number of claims for product inclusion (default: 10). Example: 50"] = None,
) -> str:
    """[Q13] Average Days Between Sale and Warranty Claim by Product."""
    errors = []
    conditions = []
    if category_name:
        try:
            conditions.append(f"c.category_name = {_lit(_enum(category_name, VALID_CATEGORIES, 'category_name'))}")
        except ValueError as e:
            errors.append(str(e))
    if repair_status:
        try:
            conditions.append(f"w.repair_status = {_lit(_enum(repair_status, VALID_REPAIR_STATUSES, 'repair_status'))}")
        except ValueError as e:
            errors.append(str(e))
    mc = _pos_int(min_claims, "min_claims", default=10)
    if errors:
        return _err(errors)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = (
        f"SELECT p.Product_Name, c.category_name, COUNT(w.claim_id) AS total_claims, "
        f"ROUND(AVG(date_diff('day', date_parse(s.sale_date, '%d-%m-%Y'), date_parse(w.claim_date, '%Y-%m-%d'))), 0) AS avg_days_to_claim, "
        f"MIN(date_diff('day', date_parse(s.sale_date, '%d-%m-%Y'), date_parse(w.claim_date, '%Y-%m-%d'))) AS min_days_to_claim, "
        f"MAX(date_diff('day', date_parse(s.sale_date, '%d-%m-%Y'), date_parse(w.claim_date, '%Y-%m-%d'))) AS max_days_to_claim "
        f"FROM warranty w JOIN sales s ON w.sale_id = s.sale_id "
        f"JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN category c ON p.Category_ID = c.category_id "
        f"{where} GROUP BY p.Product_Name, c.category_name "
        f"HAVING COUNT(w.claim_id) >= {mc} ORDER BY avg_days_to_claim ASC"
    )
    return _ok(sql, {"query_id": "Q13", "output_columns": ["Product_Name", "category_name", "total_claims", "avg_days_to_claim", "min_days_to_claim", "max_days_to_claim"]})


# ── Q14: Store Category Sales Mix ─────────────────────────────────────────
@mcp.tool(
    name="store_category_sales_mix",
    description=(
        "Breaks down a specific store's sales into category-level revenue and percentage contribution. "
        "Shows which product categories drive each store's business. Used by store managers and "
        "visual merchandising teams to optimize floor layout and inventory allocation."
    ),
    tags={"sales", "stores", "category", "mix", "merchandising", "revenue"},
)
def store_category_sales_mix(
    store_name: Annotated[str, "Exact name of the Apple store. Example: Apple Fifth Avenue"],
    start_date: Annotated[Optional[str], "Start of analysis period (YYYY-MM-DD, optional). Example: 2023-01-01"] = None,
    end_date: Annotated[Optional[str], "End of analysis period (YYYY-MM-DD, optional). Example: 2023-12-31"] = None,
) -> str:
    """[Q14] Cross-Category Sales Mix for a Specific Store."""
    if not store_name or not store_name.strip():
        return _err(["'store_name' is required."])
    errors = []
    sn = _s(store_name.strip())
    sd = "2019-01-01"; ed = "2026-12-31"
    if start_date:
        try:
            sd = _date(start_date, "start_date")
        except ValueError as e:
            errors.append(str(e))
    if end_date:
        try:
            ed = _date(end_date, "end_date")
        except ValueError as e:
            errors.append(str(e))
    if errors:
        return _err(errors)
    sql = (
        f"SELECT st.Store_Name, c.category_name, COUNT(s.sale_id) AS transactions, "
        f"SUM(s.quantity) AS total_units, SUM(s.quantity * p.Price) AS category_revenue, "
        f"ROUND(SUM(s.quantity * p.Price) * 100.0 / SUM(SUM(s.quantity * p.Price)) OVER (), 2) AS revenue_pct "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN category c ON p.Category_ID = c.category_id "
        f"JOIN stores st ON s.store_id = st.Store_ID "
        f"WHERE st.Store_Name = '{sn}' "
        f"AND date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)} "
        f"GROUP BY st.Store_Name, c.category_name ORDER BY category_revenue DESC"
    )
    return _ok(sql, {"query_id": "Q14", "output_columns": ["Store_Name", "category_name", "transactions", "total_units", "category_revenue", "revenue_pct"]})


# ── Q15: High-Value Transactions ──────────────────────────────────────────
@mcp.tool(
    name="high_value_transactions",
    description=(
        "Identifies individual sale transactions where line-item revenue (quantity x price) exceeds "
        "a specified threshold. Includes full context: product, store, date, and warranty claim if any. "
        "Used by finance and audit teams to investigate high-value transactions for compliance and fraud review."
    ),
    tags={"sales", "transactions", "finance", "audit", "compliance", "high-value"},
)
def high_value_transactions(
    min_revenue: Annotated[int, "Minimum transaction revenue threshold (quantity x price). Example: 10000"],
    country: Annotated[Optional[str], "Filter to a specific country (optional). Example: Germany"] = None,
    category_name: Annotated[Optional[str], "Filter to a specific category (optional). Example: Laptop"] = None,
    start_date: Annotated[Optional[str], "Start of period (YYYY-MM-DD, optional). Example: 2023-07-01"] = None,
    end_date: Annotated[Optional[str], "End of period (YYYY-MM-DD, optional). Example: 2023-09-30"] = None,
    limit: Annotated[Optional[int], "Maximum rows to return (default: 200). Example: 50"] = None,
) -> str:
    """[Q15] High-Value Transactions Above a Revenue Threshold."""
    errors = []
    try:
        mr = _pos_int(min_revenue, "min_revenue")
    except ValueError as e:
        errors.append(str(e)); mr = None
    conditions = [f"s.quantity * p.Price >= {mr}" if mr else "1=0"]
    if country:
        try:
            conditions.append(f"st.Country = {_lit(_enum(country, VALID_COUNTRIES, 'country'))}")
        except ValueError as e:
            errors.append(str(e))
    if category_name:
        try:
            conditions.append(f"c.category_name = {_lit(_enum(category_name, VALID_CATEGORIES, 'category_name'))}")
        except ValueError as e:
            errors.append(str(e))
    sd = "2019-01-01"; ed = "2026-12-31"
    if start_date:
        try:
            sd = _date(start_date, "start_date")
        except ValueError as e:
            errors.append(str(e))
    if end_date:
        try:
            ed = _date(end_date, "end_date")
        except ValueError as e:
            errors.append(str(e))
    conditions.append(f"date_parse(s.sale_date, '%d-%m-%Y') BETWEEN DATE {_lit(sd)} AND DATE {_lit(ed)}")
    lim = _pos_int(limit, "limit", default=200)
    if errors:
        return _err(errors)
    sql = (
        f"SELECT s.sale_id, s.sale_date, s.quantity, p.Product_Name, p.Price, "
        f"s.quantity * p.Price AS line_revenue, c.category_name, "
        f"st.Store_Name, st.City, st.Country, w.claim_id, w.repair_status "
        f"FROM sales s JOIN products p ON s.product_id = p.Product_ID "
        f"JOIN category c ON p.Category_ID = c.category_id "
        f"JOIN stores st ON s.store_id = st.Store_ID "
        f"LEFT JOIN warranty w ON s.sale_id = w.sale_id "
        f"WHERE {' AND '.join(conditions)} "
        f"ORDER BY line_revenue DESC LIMIT {lim}"
    )
    return _ok(sql, {"query_id": "Q15", "output_columns": ["sale_id", "sale_date", "quantity", "Product_Name", "Price", "line_revenue", "category_name", "Store_Name", "City", "Country", "claim_id", "repair_status"]})


# ── generate_sql: Fallback for ad-hoc queries ─────────────────────────────
@mcp.tool(
    name="generate_sql",
    description=(
        "Fallback SQL generator for ad-hoc queries NOT covered by the 15 predefined tools. "
        "Accepts a plain-English description and a complete SQL SELECT statement, validates it "
        "for safety (SELECT-only, known tables only), and returns the validated query. "
        "Use ONLY when no predefined tool (Q01-Q15) matches the user's request."
    ),
    tags={"sql", "ad-hoc", "fallback", "custom", "generate"},
)
def generate_sql(
    query_description: Annotated[str, "Plain-English description of what data the user wants. Example: Average product price per category"],
    sql_query: Annotated[str, "A complete SQL SELECT statement using the apple retail schema."],
) -> str:
    """Fallback SQL generator for ad-hoc queries NOT covered by Q01-Q15.

    Schema: sales (s), products (p), stores (st), category (c), warranty (w).
    sale_date is DD-MM-YYYY — use date_parse(sale_date, '%d-%m-%Y'). Only SELECT queries allowed.
    Use Trino/Athena SQL syntax (date_parse, date_format, date_diff, year, quarter).
    """
    description = (query_description or "").strip()
    sql = (sql_query or "").strip()
    if not description:
        return json.dumps({"status": "error", "error": "Missing 'query_description'."}, indent=2)
    if not sql:
        return json.dumps({
            "status": "needs_sql",
            "message": "Provide a 'sql_query' SELECT statement.",
            "tables": {
                "sales (s)": "sale_id, sale_date [DD-MM-YYYY], store_id, product_id, quantity",
                "products (p)": "Product_ID, Product_Name, Category_ID, Launch_Date, Price",
                "stores (st)": "Store_ID, Store_Name, City, Country",
                "category (c)": "category_id, category_name",
                "warranty (w)": "claim_id, claim_date, sale_id, repair_status",
            },
        }, indent=2)
    issues = _validate_sql_safety(sql)
    blocking = [i for i in issues if "Blocked" in i or "must start" in i]
    if blocking:
        return json.dumps({"status": "error", "errors": blocking}, indent=2)
    warnings = [i for i in issues if i not in blocking] or None
    return json.dumps({
        "status": "success",
        "query_description": description,
        "sql": sql,
        "warnings": warnings,
        "note": "Custom query - verify correctness before execution.",
    }, indent=2)


# ── MCP Resource ───────────────────────────────────────────────────────────
@mcp.resource(
    uri="resource://apple-retail/config",
    name="Apple Retail SQL Config",
    description="Returns server configuration: app name, version, environment, and available query IDs (Q01-Q15).",
)
async def get_server_config():
    return {
        "appName": "apple-retail-sql",
        "version": "2.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "timezone": "UTC",
        "tools": 16,
        "predefinedQueries": [f"Q{i:02d}" for i in range(1, 16)],
    }
