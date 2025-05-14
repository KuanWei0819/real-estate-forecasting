import boto3
import os
from dotenv import load_dotenv

load_dotenv()  # if you're using a .env file

def upload_file_to_s3(local_path, bucket_name, s3_key):
    s3 = boto3.client('s3')
    
    try:
        s3.upload_file(Filename=local_path, Bucket=bucket_name, Key=s3_key)
        print(f"✅ Uploaded {local_path} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
