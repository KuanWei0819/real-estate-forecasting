# airflow/dags/clean_housing_data.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
from pathlib import Path

# 🔧 Add src/ to import path
sys.path.append("/opt/airflow/src")

# ✅ Import cleaning and S3 upload functions
from data.transform_housing_data import run_cleaning_pipeline
from data.upload_to_s3 import upload_file_to_s3

# ✅ Define DAG-level constants
local_input_path = "/opt/airflow/data/raw/Housing.csv"
local_output_path = "/opt/airflow/data/clean/Housing_cleaned.csv"
bucket_name = "realestateforecasting"
s3_key = "clean/Housing_cleaned.csv"

def clean_and_upload():
    # Step 1: Clean the local CSV
    run_cleaning_pipeline(local_input_path, local_output_path)

    # Step 2: Upload cleaned file to S3
    upload_file_to_s3(local_output_path, bucket_name, s3_key)

# Default args for the DAG
default_args = {
    "start_date": datetime(2023, 1, 1),
    "catchup": False
}

# Define the DAG
with DAG(
    dag_id="clean_and_upload_housing_data",
    schedule_interval=None,
    default_args=default_args,
    description="Clean raw housing data and upload the result to S3",
) as dag:

    clean_and_upload_task = PythonOperator(
        task_id="clean_and_upload",
        python_callable=clean_and_upload
    )
