-- ============================================
-- Apple Analytics - Athena Table Definitions
-- ============================================
-- Run these in Athena Query Editor if you prefer SQL over Python

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS apple_analytics_db
COMMENT 'Apple Analytics Data Lake'
LOCATION 's3://your-analytics-data-bucket/apple-analytics/';


-- Step 2: Create Sales Table (Fact Table - Partitioned by date)
CREATE EXTERNAL TABLE IF NOT EXISTS apple_analytics_db.sales (
    sale_id STRING,
    sale_date STRING,
    store_id STRING,
    product_id STRING,
    quantity BIGINT
)
STORED AS PARQUET
LOCATION 's3://your-analytics-data-bucket/apple-analytics/sales/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'classification'='parquet'
);

-- For partitioned version (recommended for large datasets):
CREATE EXTERNAL TABLE IF NOT EXISTS apple_analytics_db.sales_partitioned (
    sale_id STRING,
    store_id STRING,
    product_id STRING,
    quantity BIGINT
)
PARTITIONED BY (
    sale_date STRING
)
STORED AS PARQUET
LOCATION 's3://your-analytics-data-bucket/apple-analytics/sales_partitioned/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'classification'='parquet'
);

-- Load partitions (run after data upload)
MSCK REPAIR TABLE apple_analytics_db.sales_partitioned;


-- Step 3: Create Products Table (Dimension)
CREATE EXTERNAL TABLE IF NOT EXISTS apple_analytics_db.products (
    product_id STRING,
    product_name STRING,
    category_id STRING,
    launch_date STRING,
    price BIGINT
)
STORED AS PARQUET
LOCATION 's3://your-analytics-data-bucket/apple-analytics/products/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'classification'='parquet'
);


-- Step 4: Create Stores Table (Dimension)
CREATE EXTERNAL TABLE IF NOT EXISTS apple_analytics_db.stores (
    store_id STRING,
    store_name STRING,
    city STRING,
    country STRING
)
STORED AS PARQUET
LOCATION 's3://your-analytics-data-bucket/apple-analytics/stores/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'classification'='parquet'
);


-- Step 5: Create Categories Table (Dimension)
CREATE EXTERNAL TABLE IF NOT EXISTS apple_analytics_db.categories (
    category_id STRING,
    category_name STRING
)
STORED AS PARQUET
LOCATION 's3://your-analytics-data-bucket/apple-analytics/categories/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'classification'='parquet'
);


-- Step 6: Create Warranty Table
CREATE EXTERNAL TABLE IF NOT EXISTS apple_analytics_db.warranty (
    claim_id STRING,
    claim_date STRING,
    sale_id STRING,
    repair_status STRING
)
STORED AS PARQUET
LOCATION 's3://your-analytics-data-bucket/apple-analytics/warranty/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'classification'='parquet'
);


-- ============================================
-- Test Queries
-- ============================================

-- Verify row counts
SELECT 'sales' as table_name, COUNT(*) as row_count FROM apple_analytics_db.sales
UNION ALL
SELECT 'products', COUNT(*) FROM apple_analytics_db.products
UNION ALL
SELECT 'stores', COUNT(*) FROM apple_analytics_db.stores
UNION ALL
SELECT 'categories', COUNT(*) FROM apple_analytics_db.categories
UNION ALL
SELECT 'warranty', COUNT(*) FROM apple_analytics_db.warranty;


-- Sample joined query
SELECT 
    s.sale_date,
    p.product_name,
    c.category_name,
    st.country,
    s.quantity,
    s.quantity * p.price as revenue
FROM apple_analytics_db.sales s
JOIN apple_analytics_db.products p ON s.product_id = p.product_id
JOIN apple_analytics_db.categories c ON p.category_id = c.category_id
JOIN apple_analytics_db.stores st ON s.store_id = st.store_id
LIMIT 10;


-- Revenue by product and country
SELECT 
    p.product_name,
    st.country,
    SUM(s.quantity * p.price) as total_revenue,
    SUM(s.quantity) as units_sold
FROM apple_analytics_db.sales s
JOIN apple_analytics_db.products p ON s.product_id = p.product_id
JOIN apple_analytics_db.stores st ON s.store_id = st.store_id
GROUP BY p.product_name, st.country
ORDER BY total_revenue DESC
LIMIT 20;
