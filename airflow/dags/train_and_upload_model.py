# airflow/dags/train_and_upload_model.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
from pathlib import Path


# Add src/ to import path for Docker-based Airflow

sys.path.append("/opt/airflow/src")

# Import your training and S3 upload functions
from model.train_model import train_model
from data.upload_to_s3 import upload_file_to_s3

# Paths inside the Airflow container
input_path = "/opt/airflow/data/clean/Housing_cleaned.csv"
model_output_path = "/opt/airflow/models/housing_price_model.pkl"
s3_key = "models/housing_price_model.pkl"
bucket_name = "realestateforecasting"

def train_and_save():
    train_model(input_path, model_output_path)

def upload_model():
    upload_file_to_s3(model_output_path, bucket_name, s3_key)

default_args = {
    "start_date": datetime(2023, 1, 1),
    "catchup": False
}

with DAG(
    dag_id="train_and_upload_model",
    schedule_interval=None,
    default_args=default_args,
    description="Train housing price model and upload to S3",
) as dag:

    train_task = PythonOperator(
        task_id="train_model",
        python_callable=train_and_save
    )

    upload_task = PythonOperator(
        task_id="upload_model_to_s3",
        python_callable=upload_model
    )

    train_task >> upload_task
