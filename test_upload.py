from src.data.upload_to_s3 import upload_file_to_s3

upload_file_to_s3(
    local_path="data/raw/Housing.csv",
    bucket_name="realestateforecasting",         # 🔁 Replace with your bucket
    s3_key="raw/Housing.csv"
)