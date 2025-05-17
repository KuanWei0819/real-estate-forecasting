from fastapi import FastAPI
from pydantic import BaseModel
import boto3
import joblib
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

app = FastAPI()


import boto3

sts = boto3.client("sts")
print("IAM identity being used:", sts.get_caller_identity())

# --- Load the model from S3 ---
def load_model_from_s3():
    s3 = boto3.client("s3")
    bucket = "realestateforecasting"
    key = "models/housing_price_model.pkl" # replace with your actual bucket name
    local_model_path = "/tmp/price_model.pkl"

    try:
        if not Path(local_model_path).exists():
            s3.download_file(bucket, key, local_model_path)
    except Exception as e:
        print("Error downloading model:", e)
        raise

    return joblib.load(local_model_path)

model = load_model_from_s3()

# --- Define input schema ---
class InputData(BaseModel):
    area: float
    bedrooms: int
    bathrooms: int
    stories: int
    mainroad: str
    guestroom: str
    basement: str
    hotwaterheating: str
    airconditioning: str
    parking: int
    prefarea: str
    furnishingstatus: str

# --- Prediction endpoint ---
@app.post("/predict")
def predict(data: InputData):
    input_df = pd.DataFrame([{
        "area": data.area,
        "bedrooms": data.bedrooms,
        "bathrooms": data.bathrooms,
        "stories": data.stories,
        "mainroad": data.mainroad,
        "guestroom": data.guestroom,
        "basement": data.basement,
        "hotwaterheating": data.hotwaterheating,
        "airconditioning": data.airconditioning,
        "parking": data.parking,
        "prefarea": data.prefarea,
        "furnishingstatus": data.furnishingstatus
    }])
    prediction = model.predict(input_df)[0]
    return {"estimated_price": round(prediction, 2)}

# --- Health check ---
@app.get("/health")
def health_check():
    return {"status": "ok"}
