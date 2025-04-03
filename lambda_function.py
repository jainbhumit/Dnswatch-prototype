import json
import boto3
import pg8000
import csv
import io
import os

# Environment variables
DB_HOST = os.getenv("DB_HOST", "your-rds-endpoint")
DB_NAME = os.getenv("DB_NAME", "your-db-name")
DB_USER = os.getenv("DB_USER", "your-db-user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your-db-password")
DB_PORT = os.getenv("DB_PORT", "5432")
TABLE_NAME = os.getenv("TABLE_NAME", "your_table_name")

# Initialize S3 client
s3 = boto3.client("s3")


def lambda_handler(event, context):
    try:
        # Extract S3 key from event
        s3_key = event["s3_key"]["S3Key"]
        s3_parts = s3_key.replace("s3://", "").split("/", 1)
        bucket_name = s3_parts[0]
        object_key = s3_parts[1]

        print(f"Downloading {object_key} from bucket {bucket_name}")

        # Download CSV file from S3
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        csv_content = response["Body"].read().decode("utf-8")

        # Read CSV using Python's built-in CSV module
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)

        if not rows:
            return {
                "statusCode": 200,
                "body": json.dumps("No data found in CSV file")
            }

        # Connect to PostgreSQL using pg8000
        conn = pg8000.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=int(DB_PORT)
        )
        cursor = conn.cursor()

        # Get column names from first row
        columns = ", ".join(rows[0].keys())
        values_placeholder = ", ".join(["%s"] * len(rows[0]))
        insert_query = f"INSERT INTO {TABLE_NAME} ({columns}) VALUES ({values_placeholder})"

        # Insert data
        for row in rows:
            cursor.execute(insert_query, list(row.values()))

        # Commit transaction
        conn.commit()

        # Close connection
        cursor.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps(f"Inserted {len(rows)} rows into {TABLE_NAME}")
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }