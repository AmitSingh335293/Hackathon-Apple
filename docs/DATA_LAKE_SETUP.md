# 🗄️ Data Lake Setup Guide

---

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured
3. **Python dependencies**:
   ```bash
   pip install boto3 pandas pyarrow
   ```

4. **IAM Permissions Required**:
   - S3: `PutObject`, `GetObject`, `ListBucket`
   - Glue: `CreateDatabase`, `CreateTable`, `UpdateTable`
   - Athena: `StartQueryExecution`, `GetQueryResults`
   - Lake Formation (optional): `GrantPermissions`

---

## 🏗️ Architecture

```
┌─────────────┐
│   CSV/Raw   │
│    Data     │
└──────┬──────┘
       │ Convert to Parquet
       ↓
┌─────────────┐
│   Amazon    │
│     S3      │  ← Stores Parquet files
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  AWS Glue   │  ← Data Catalog (metadata)
│   Catalog   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Amazon    │  ← Query Engine
│   Athena    │
└─────────────┘
```

---

## 🚀 Quick Setup (3 Steps)

### **Step 1: Prepare Your Data**

Place your CSV files in `data/raw/`:
```
data/raw/
├── sales.csv
├── products.csv
├── stores.csv
├── categories.csv
└── warranty.csv
```

**Expected Formats:**

**sales.csv**
```csv
sale_id,sale_date,store_id,product_id,quantity
S001,2024-01-15,ST001,P001,2
S002,2024-01-15,ST002,P003,1
```

**products.csv**
```csv
product_id,product_name,category_id,launch_date,price
P001,iPhone 15 Pro,C001,2023-09-22,999
P002,MacBook Air M3,C002,2024-03-04,1099
```

**stores.csv**
```csv
store_id,store_name,city,country
ST001,Apple Fifth Avenue,New York,USA
ST002,Apple Regent Street,London,UK
```

**categories.csv**
```csv
category_id,category_name
C001,iPhone
C002,Mac
C003,iPad
```

**warranty.csv**
```csv
claim_id,claim_date,sale_id,repair_status
W001,2024-02-10,S001,Completed
W002,2024-03-05,S015,Pending
```

---

### **Step 2: Create S3 Bucket**

```bash
# Create bucket
aws s3 mb s3://apple-analytics-data-lake --region us-east-1

# Enable versioning (recommended)
aws s3api put-bucket-versioning \
    --bucket apple-analytics-data-lake \
    --versioning-configuration Status=Enabled

# Create folders
aws s3api put-object --bucket apple-analytics-data-lake --key apple-analytics/sales/
aws s3api put-object --bucket apple-analytics-data-lake --key apple-analytics/products/
aws s3api put-object --bucket apple-analytics-data-lake --key apple-analytics/stores/
aws s3api put-object --bucket apple-analytics-data-lake --key apple-analytics/categories/
aws s3api put-object --bucket apple-analytics-data-lake --key apple-analytics/warranty/
aws s3api put-object --bucket apple-analytics-data-lake --key athena-results/
```

---

### **Step 3: Run Setup Script**

**Option A: Python Script (Recommended)**
```bash
cd scripts
python setup_data_lake.py \
    --bucket apple-analytics-data-lake \
    --region us-east-1 \
    --database apple_analytics_db \
    --test
```

**Option B: Manual SQL (Athena Console)**
1. Open [AWS Athena Console](https://console.aws.amazon.com/athena/)
2. Copy SQL from `scripts/create_athena_tables.sql`
3. Replace `your-analytics-data-bucket` with your bucket name
4. Execute each CREATE TABLE statement

**Option C: AWS CLI**
```bash
# Upload data manually
aws s3 sync data/raw/ s3://apple-analytics-data-lake/apple-analytics/sales/ \
    --exclude "*" --include "sales.csv"

# Create database
aws glue create-database \
    --database-input '{"Name": "apple_analytics_db", "Description": "Apple Analytics"}'
```

---

## 📊 Table Schemas

### Sales (Fact Table)
```sql
sale_id       STRING      -- Unique sale identifier
sale_date     STRING      -- Format: YYYY-MM-DD
store_id      STRING      -- FK to stores
product_id    STRING      -- FK to products
quantity      BIGINT      -- Units sold
```

### Products (Dimension)
```sql
product_id    STRING      -- PK
product_name  STRING      -- e.g., "iPhone 15 Pro"
category_id   STRING      -- FK to categories
launch_date   STRING      -- Format: YYYY-MM-DD
price         BIGINT      -- Price in USD
```

### Stores (Dimension)
```sql
store_id      STRING      -- PK
store_name    STRING      -- e.g., "Apple Fifth Avenue"
city          STRING
country       STRING
```

### Categories (Dimension)
```sql
category_id   STRING      -- PK
category_name STRING      -- e.g., "iPhone", "Mac", "iPad"
```

### Warranty
```sql
claim_id      STRING      -- PK
claim_date    STRING      -- Format: YYYY-MM-DD
sale_id       STRING      -- FK to sales
repair_status STRING      -- Values: Completed, Rejected, Pending, In Progress
```

---

## 🔍 Verification

### Test Queries

**1. Check row counts:**
```sql
SELECT COUNT(*) as total_sales FROM apple_analytics_db.sales;
```

**2. Sample data:**
```sql
SELECT * FROM apple_analytics_db.sales LIMIT 10;
```

**3. Join test:**
```sql
SELECT 
    s.sale_id,
    s.sale_date,
    p.product_name,
    st.country,
    s.quantity * p.price as revenue
FROM apple_analytics_db.sales s
JOIN apple_analytics_db.products p ON s.product_id = p.product_id
JOIN apple_analytics_db.stores st ON s.store_id = st.store_id
LIMIT 5;
```

**4. Aggregation test:**
```sql
SELECT 
    p.product_name,
    SUM(s.quantity) as units_sold,
    SUM(s.quantity * p.price) as total_revenue
FROM apple_analytics_db.sales s
JOIN apple_analytics_db.products p ON s.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_revenue DESC;
```

---

## ⚙️ Configuration

### Update `.env` file:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here

# Athena Configuration
ATHENA_DATABASE=apple_analytics_db
ATHENA_WORKGROUP=primary
ATHENA_OUTPUT_LOCATION=s3://apple-analytics-data-lake/athena-results/

# S3 Configuration
S3_DATA_BUCKET=apple-analytics-data-lake
S3_DATA_PREFIX=apple-analytics/
```

---

## 🎯 Data Optimization Tips

### 1. **Use Partitioning for Large Tables**

For sales table with millions of rows:
```sql
CREATE EXTERNAL TABLE sales_partitioned (
    sale_id STRING,
    store_id STRING,
    product_id STRING,
    quantity BIGINT
)
PARTITIONED BY (year STRING, month STRING)
STORED AS PARQUET
LOCATION 's3://apple-analytics-data-lake/apple-analytics/sales_partitioned/';
```

**Benefits:**
- Faster queries (scan only relevant partitions)
- Lower costs (pay for scanned data)
- Better performance for date-range queries

### 2. **Parquet vs CSV**

| Format  | Size | Query Speed | Cost |
|---------|------|-------------|------|
| CSV     | 1GB  | Slow        | $5   |
| Parquet | 200MB| Fast        | $1   |

**Always use Parquet in production!**

### 3. **Compression**

```python
# When converting to Parquet
pq.write_table(
    table, 
    'output.parquet',
    compression='SNAPPY'  # or 'GZIP', 'ZSTD'
)
```

### 4. **Create Views for Common Queries**

```sql
CREATE VIEW revenue_by_product AS
SELECT 
    p.product_name,
    c.category_name,
    SUM(s.quantity * p.price) as revenue,
    SUM(s.quantity) as units_sold
FROM sales s
JOIN products p ON s.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY p.product_name, c.category_name;
```

---

## 🔒 Security Best Practices

### 1. **Bucket Policy (S3)**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAthenaAccess",
      "Effect": "Allow",
      "Principal": {
        "Service": "athena.amazonaws.com"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::apple-analytics-data-lake/*",
        "arn:aws:s3:::apple-analytics-data-lake"
      ]
    }
  ]
}
```

### 2. **Lake Formation (Row-Level Security)**

```python
# Grant table access to specific users
import boto3

lf = boto3.client('lakeformation')

lf.grant_permissions(
    Principal={'DataLakePrincipalIdentifier': 'arn:aws:iam::123456789012:user/analyst'},
    Resource={'Table': {
        'DatabaseName': 'apple_analytics_db',
        'Name': 'sales'
    }},
    Permissions=['SELECT'],
    PermissionsWithGrantOption=[]
)
```

---

## 💰 Cost Optimization

### Athena Pricing (as of 2026)
- **$5 per TB scanned**
- Charged per query based on data scanned

### Example Costs:
| Query Type | Data Scanned | Cost |
|------------|--------------|------|
| `SELECT *` | 1 TB | $5.00 |
| Partitioned query | 10 GB | $0.05 |
| Compressed Parquet | 100 MB | $0.0005 |

### Strategies:
1. ✅ Use Parquet (80% size reduction)
2. ✅ Partition large tables
3. ✅ Use column projection (avoid `SELECT *`)
4. ✅ Set workgroup query limits
5. ✅ Cache results in Redis

---

## 🐛 Troubleshooting

### Issue: "Table not found"
```bash
# Check if database exists
aws glue get-database --name apple_analytics_db

# List tables
aws glue get-tables --database-name apple_analytics_db
```

### Issue: "Access Denied" on S3
```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket apple-analytics-data-lake

# Verify IAM permissions
aws iam get-user-policy --user-name your-user --policy-name your-policy
```

### Issue: "0 rows returned"
```bash
# Verify S3 data
aws s3 ls s3://apple-analytics-data-lake/apple-analytics/sales/

# Check Glue table location
aws glue get-table --database-name apple_analytics_db --name sales
```

---

## 📚 Next Steps

1. ✅ **Set up monitoring**: CloudWatch metrics for query performance
2. ✅ **Implement governance**: Use Lake Formation for access control
3. ✅ **Optimize costs**: Create workgroup with query limits
4. ✅ **Add metadata**: Use Glue Crawlers to auto-detect schema changes
5. ✅ **Test at scale**: Load production-size data and benchmark

---

## 📞 Resources

- [AWS Athena Documentation](https://docs.aws.amazon.com/athena/)
- [AWS Glue Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html)
- [Parquet Format Guide](https://parquet.apache.org/docs/)
- [Lake Formation Security](https://docs.aws.amazon.com/lake-formation/)
