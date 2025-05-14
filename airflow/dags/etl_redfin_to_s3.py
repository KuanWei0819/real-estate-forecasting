print("✅ DAG upload_local_to_s3.py loaded.")

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
from pathlib import Path

# ✅ Add src/ to import path so it works inside Docker
sys.path.append("/opt/airflow/src")

try:
    from data.upload_to_s3 import upload_file_to_s3
    print("✅ Successfully imported upload_file_to_s3")
except Exception as e:
    print(f"❌ Import failed in DAG: {e}")

def upload_task():
    # ✅ This path is inside the container, mapped from your local data/
    local_file = Path("/opt/airflow/data/raw/Housing.csv")
    bucket_name = "realestateforecasting"
    s3_key = "raw/Housing.csv"

    upload_file_to_s3(local_file, bucket_name, s3_key)

default_args = {
    "start_date": datetime(2023, 1, 1),
    "catchup": False
}

with DAG(
    dag_id="upload_local_to_s3",
    schedule_interval=None,
    default_args=default_args,
    description="Upload Housing.csv to S3 using custom src/ function",
) as dag:

    task = PythonOperator(
        task_id="upload_to_s3",
        python_callable=upload_task
    )
