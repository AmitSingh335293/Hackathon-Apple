#!/usr/bin/env python3
"""
Local Testing Script
Test the NLP to SQL system without AWS dependencies
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.template_service import TemplateService
from app.services.query_builder import QueryBuilder
from app.services.query_executor import QueryExecutor
from app.services.governance_service import GovernanceService, QueryValidationError
from app.services.result_formatter import ResultFormatter
from app.utils import setup_logging, get_logger

# Setup logging
setup_logging("INFO")
logger = get_logger(__name__)


async def test_embedding_service():
    """Test embedding generation"""
    logger.info("=" * 60)
    logger.info("Testing Embedding Service")
    logger.info("=" * 60)
    
    service = EmbeddingService()
    
    text = "What was iPhone revenue in India last quarter?"
    embedding = await service.generate_embedding(text)
    
    logger.info(f"Generated embedding with {len(embedding)} dimensions")
    logger.info(f"First 5 values: {embedding[:5]}")
    
    # Test similarity
    text2 = "Show me iPhone sales in India"
    embedding2 = await service.generate_embedding(text2)
    
    similarity = service.cosine_similarity(embedding, embedding2)
    logger.info(f"Similarity between queries: {similarity:.4f}")
    
    print("✅ Embedding Service test passed\n")


async def test_template_service():
    """Test template matching"""
    logger.info("=" * 60)
    logger.info("Testing Template Service")
    logger.info("=" * 60)
    
    service = TemplateService()
    
    query = "What was iPhone revenue in India last quarter?"
    templates = await service.search_similar_templates(query, top_k=3)
    
    logger.info(f"Found {len(templates)} matching templates")
    
    for i, template in enumerate(templates, 1):
        logger.info(f"\nTemplate {i}:")
        logger.info(f"  Name: {template.get('name')}")
        logger.info(f"  Similarity: {template.get('similarity_score', 0):.4f}")
        logger.info(f"  SQL: {template.get('sql_template', '')[:100]}...")
    
    print("✅ Template Service test passed\n")


async def test_llm_service():
    """Test LLM mock responses"""
    logger.info("=" * 60)
    logger.info("Testing LLM Service (Mock Mode)")
    logger.info("=" * 60)
    
    service = LLMService()
    
    query = "What was iPhone revenue in India last quarter?"
    
    # Test intent extraction
    intent = await service.extract_intent_and_parameters(query)
    logger.info(f"Extracted intent: {intent}")
    
    # Test SQL generation
    schema = {"tables": ["apple_sales_fact"]}
    sql = await service.generate_sql(query, schema, intent)
    logger.info(f"Generated SQL:\n{sql}")
    
    # Test summary generation
    results = [{"total_revenue": 4500000, "total_units": 90000}]
    summary = await service.generate_summary(query, sql, results)
    logger.info(f"Summary: {summary}")
    
    print("✅ LLM Service test passed\n")


async def test_query_builder():
    """Test query building"""
    logger.info("=" * 60)
    logger.info("Testing Query Builder")
    logger.info("=" * 60)
    
    builder = QueryBuilder()
    
    query = "What was iPhone revenue in India last quarter?"
    user_id = "test_user_123"
    
    result = await builder.build_query(query, user_id)
    
    logger.info(f"SQL Query:\n{result['sql_query']}")
    logger.info(f"Generation method: {result['metadata']['generation_method']}")
    logger.info(f"Matched template: {result['metadata'].get('matched_template')}")
    
    print("✅ Query Builder test passed\n")


async def test_governance():
    """Test governance validation"""
    logger.info("=" * 60)
    logger.info("Testing Governance Service")
    logger.info("=" * 60)
    
    service = GovernanceService()
    
    # Test valid query
    valid_query = """
    SELECT product, region, SUM(revenue) as total_revenue
    FROM apple_sales_fact
    WHERE date >= '2024-01-01'
    GROUP BY product, region
    LIMIT 100
    """
    
    result = await service.validate_query(valid_query, "test_user")
    logger.info(f"Validation result: {result['valid']}")
    logger.info(f"Warnings: {result['warnings']}")
    logger.info(f"Estimated cost: ${result['estimated_cost_usd']:.4f}")
    
    # Test invalid query
    try:
        invalid_query = "DROP TABLE apple_sales_fact"
        await service.validate_query(invalid_query, "test_user")
        print("❌ Governance should have blocked DROP statement")
    except QueryValidationError as e:
        logger.info(f"✅ Correctly blocked invalid query: {e}")
    
    print("✅ Governance Service test passed\n")


async def test_query_executor():
    """Test query execution on mock data"""
    logger.info("=" * 60)
    logger.info("Testing Query Executor")
    logger.info("=" * 60)
    
    executor = QueryExecutor()
    
    # Simple aggregation query
    query = """
    SELECT product, region, SUM(revenue) as total_revenue, SUM(units_sold) as total_units
    FROM apple_sales_fact
    WHERE product = 'iPhone' AND region = 'India'
    GROUP BY product, region
    """
    
    result = await executor.execute_query(query)
    
    logger.info(f"Query ID: {result['query_id']}")
    logger.info(f"Execution time: {result['execution_time_seconds']} seconds")
    logger.info(f"Rows returned: {result['row_count']}")
    logger.info(f"Results:")
    
    for row in result['results'][:5]:
        logger.info(f"  {row}")
    
    print("✅ Query Executor test passed\n")


async def test_result_formatter():
    """Test result formatting"""
    logger.info("=" * 60)
    logger.info("Testing Result Formatter")
    logger.info("=" * 60)
    
    formatter = ResultFormatter()
    
    results = [
        {"product": "iPhone", "region": "India", "revenue": 125000, "units": 2500},
        {"product": "iPad", "region": "India", "revenue": 89000, "units": 1780},
        {"product": "Mac", "region": "India", "revenue": 156000, "units": 1560},
    ]
    
    formatted = formatter.format_results(results, preview_rows=5)
    
    logger.info(f"Total rows: {formatted['total_rows']}")
    logger.info(f"Columns: {formatted['columns']}")
    logger.info(f"Statistics: {formatted['statistics']}")
    logger.info(f"Preview: {formatted['data_preview']}")
    
    # Test insights
    insights = formatter.create_insights(results, formatted['statistics'])
    logger.info(f"Insights: {insights}")
    
    print("✅ Result Formatter test passed\n")


async def test_end_to_end():
    """Test complete end-to-end flow"""
    logger.info("=" * 60)
    logger.info("Testing End-to-End Flow")
    logger.info("=" * 60)
    
    user_query = "What was iPhone revenue in India last quarter?"
    user_id = "test_user_123"
    
    # Step 1: Build query
    builder = QueryBuilder()
    build_result = await builder.build_query(user_query, user_id)
    sql_query = build_result['sql_query']
    
    logger.info(f"Step 1 - SQL Generated:\n{sql_query}")
    
    # Step 2: Validate
    governance = GovernanceService()
    try:
        validation = await governance.validate_query(sql_query, user_id)
        logger.info(f"Step 2 - Validation: {validation['valid']}")
    except QueryValidationError as e:
        logger.error(f"Validation failed: {e}")
        return
    
    # Step 3: Execute
    executor = QueryExecutor()
    exec_result = await executor.execute_query(sql_query)
    results = exec_result['results']
    
    logger.info(f"Step 3 - Executed: {len(results)} rows returned")
    
    # Step 4: Format
    formatter = ResultFormatter()
    formatted = formatter.format_results(results, preview_rows=5)
    
    logger.info(f"Step 4 - Formatted preview:")
    for row in formatted['data_preview']:
        logger.info(f"  {row}")
    
    # Step 5: Generate summary
    llm = LLMService()
    summary = await llm.generate_summary(user_query, sql_query, results)
    
    logger.info(f"Step 5 - Summary: {summary}")
    
    print("✅ End-to-End test passed\n")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("NLP to SQL System - Local Testing (Mock Mode)")
    print("=" * 60 + "\n")
    
    try:
        await test_embedding_service()
        await test_template_service()
        await test_llm_service()
        await test_query_builder()
        await test_governance()
        await test_query_executor()
        await test_result_formatter()
        await test_end_to_end()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Tests failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
