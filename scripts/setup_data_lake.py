"""
Data Lake Setup Script
Uploads data to S3 and creates Athena tables with Glue Data Catalog
"""

import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
import json
from typing import Dict, List
import sys

# Configuration
S3_BUCKET = "your-analytics-data-bucket"  # Change this
S3_PREFIX = "apple-analytics/"
GLUE_DATABASE = "apple_analytics_db"
AWS_REGION = "us-east-1"

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
glue_client = boto3.client('glue', region_name=AWS_REGION)
athena_client = boto3.client('athena', region_name=AWS_REGION)


def create_glue_database():
    """Create Glue database if it doesn't exist"""
    try:
        glue_client.create_database(
            DatabaseInput={
                'Name': GLUE_DATABASE,
                'Description': 'Apple Analytics Data Lake'
            }
        )
        print(f"✅ Created Glue database: {GLUE_DATABASE}")
    except glue_client.exceptions.AlreadyExistsException:
        print(f"ℹ️  Glue database {GLUE_DATABASE} already exists")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)


def upload_csv_to_s3_as_parquet(
    csv_path: str,
    table_name: str,
    partition_cols: List[str] = None
) -> str:
    """
    Convert CSV to Parquet and upload to S3
    
    Args:
        csv_path: Local path to CSV file
        table_name: Name of the table
        partition_cols: Columns to partition by (optional)
    
    Returns:
        S3 URI of the uploaded data
    """
    print(f"\n📤 Processing {table_name}...")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"   Rows: {len(df):,}")
    
    # Convert to Parquet
    table = pa.Table.from_pandas(df)
    
    # S3 path
    s3_key = f"{S3_PREFIX}{table_name}/"
    
    # Upload to S3
    if partition_cols:
        # Partitioned upload
        pq.write_to_dataset(
            table,
            root_path=f"s3://{S3_BUCKET}/{s3_key}",
            partition_cols=partition_cols,
            filesystem=pa.fs.S3FileSystem()
        )
    else:
        # Single file upload with compression
        local_parquet = f"/tmp/{table_name}.parquet"
        pq.write_table(
            table, 
            local_parquet,
            compression='snappy',
            use_dictionary=True,
            write_statistics=True
        )
        
        # Show file size
        file_size_mb = Path(local_parquet).stat().st_size / (1024 * 1024)
        print(f"   📦 Parquet size: {file_size_mb:.2f} MB (compressed)")
        
        s3_client.upload_file(
            local_parquet,
            S3_BUCKET,
            f"{s3_key}data.parquet"
        )
        Path(local_parquet).unlink()
    
    s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
    print(f"   ✅ Uploaded to {s3_uri}")
    
    return s3_uri


def create_athena_table(table_name: str, schema: Dict, s3_location: str, partition_keys: List[Dict] = None):
    """
    Create Athena table via Glue Data Catalog
    
    Args:
        table_name: Name of the table
        schema: Column definitions
        s3_location: S3 URI for table data
        partition_keys: Partition column definitions (optional)
    """
    print(f"📊 Creating Athena table: {table_name}")
    
    table_input = {
        'Name': table_name,
        'Description': f'Apple Analytics - {table_name}',
        'StorageDescriptor': {
            'Columns': schema,
            'Location': s3_location,
            'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
            'SerdeInfo': {
                'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
                'Parameters': {
                    'serialization.format': '1'
                }
            }
        },
        'TableType': 'EXTERNAL_TABLE',
        'Parameters': {
            'EXTERNAL': 'TRUE',
            'parquet.compression': 'SNAPPY'
        }
    }
    
    if partition_keys:
        table_input['PartitionKeys'] = partition_keys
    
    try:
        glue_client.create_table(
            DatabaseName=GLUE_DATABASE,
            TableInput=table_input
        )
        print(f"   ✅ Table {table_name} created")
    except glue_client.exceptions.AlreadyExistsException:
        print(f"   ℹ️  Table {table_name} already exists, updating...")
        glue_client.update_table(
            DatabaseName=GLUE_DATABASE,
            TableInput=table_input
        )
    except Exception as e:
        print(f"   ❌ Error: {e}")


# Table schemas matching your data
SCHEMAS = {
    'sales': [
        {'Name': 'sale_id', 'Type': 'string'},
        {'Name': 'sale_date', 'Type': 'string'},
        {'Name': 'store_id', 'Type': 'string'},
        {'Name': 'product_id', 'Type': 'string'},
        {'Name': 'quantity', 'Type': 'bigint'}
    ],
    'products': [
        {'Name': 'product_id', 'Type': 'string'},
        {'Name': 'product_name', 'Type': 'string'},
        {'Name': 'category_id', 'Type': 'string'},
        {'Name': 'launch_date', 'Type': 'string'},
        {'Name': 'price', 'Type': 'bigint'}
    ],
    'stores': [
        {'Name': 'store_id', 'Type': 'string'},
        {'Name': 'store_name', 'Type': 'string'},
        {'Name': 'city', 'Type': 'string'},
        {'Name': 'country', 'Type': 'string'}
    ],
    'categories': [
        {'Name': 'category_id', 'Type': 'string'},
        {'Name': 'category_name', 'Type': 'string'}
    ],
    'warranty': [
        {'Name': 'claim_id', 'Type': 'string'},
        {'Name': 'claim_date', 'Type': 'string'},
        {'Name': 'sale_id', 'Type': 'string'},
        {'Name': 'repair_status', 'Type': 'string'}
    ]
}


def setup_data_lake():
    """Main setup function"""
    print("🚀 Starting Data Lake Setup\n")
    print(f"Target: s3://{S3_BUCKET}/{S3_PREFIX}")
    print(f"Database: {GLUE_DATABASE}\n")
    
    # Step 1: Create database
    # create_glue_database()
    
    # Step 2: Process each table
    # Assuming you have CSV files in data/raw/ directory
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    
    tables = ['sales', 'products', 'stores', 'categories', 'warranty']
    
    for table in tables:
        csv_file = data_dir / f"{table}.csv"
        
        if not csv_file.exists():
            print(f"⚠️  Warning: {csv_file} not found, skipping...")
            continue
        
        # Upload to S3 (no partitioning - too many unique dates)
        s3_location = upload_csv_to_s3_as_parquet(
            str(csv_file),
            table,
            partition_cols=None  # Disabled to avoid "too many partitions" error
        )
        
        # Create Athena table (no partitions)
        create_athena_table(
            table,
            SCHEMAS[table],
            s3_location,
            partition_keys=None  # No partitioning for simplified setup
        )
    
    print("\n✅ Data Lake setup complete!")
    print("\n📝 Next steps:")
    print(f"   1. Verify tables in Athena console")
    print(f"   2. Run test query: SELECT * FROM {GLUE_DATABASE}.sales LIMIT 10")
    print(f"   3. Update .env with DATABASE_NAME={GLUE_DATABASE}")


def run_test_queries():
    """Run test queries to verify setup"""
    print("\n🧪 Running test queries...\n")
    
    queries = [
        f"SELECT COUNT(*) as total_sales FROM {GLUE_DATABASE}.sales",
        f"SELECT COUNT(*) as total_products FROM {GLUE_DATABASE}.products",
        f"SELECT COUNT(*) as total_stores FROM {GLUE_DATABASE}.stores",
    ]
    
    output_location = f"s3://{S3_BUCKET}/athena-results/"
    
    for query in queries:
        try:
            response = athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': GLUE_DATABASE},
                ResultConfiguration={'OutputLocation': output_location}
            )
            print(f"✅ Query submitted: {response['QueryExecutionId']}")
        except Exception as e:
            print(f"❌ Query failed: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Apple Analytics Data Lake')
    parser.add_argument('--bucket', required=True, help='S3 bucket name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--database', default='apple_analytics_db', help='Glue database name')
    parser.add_argument('--test', action='store_true', help='Run test queries after setup')
    
    args = parser.parse_args()
    
    # Update global config
    S3_BUCKET = args.bucket
    AWS_REGION = args.region
    GLUE_DATABASE = args.database
    
    # Run setup
    setup_data_lake()
    
    if args.test:
        run_test_queries()
