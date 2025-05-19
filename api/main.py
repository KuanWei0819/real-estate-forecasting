from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
import joblib
import boto3
import shutil
import os
import sys


S3_BUCKET = "realestateforecasting"
S3_DATA_KEY = "clean/Housing_cleaned.csv"
S3_MODEL_KEY = "models/price_model.pkl"
LOCAL_MODEL_PATH = "/tmp/price_model.pkl"


# sys.path needs to be set before importing train_model
sys.path.append(str(Path(__file__).resolve().parents[1]))


# --- Load .env file (for AWS keys) ---
load_dotenv()

app = FastAPI()

# Log current IAM identity (optional for debugging)
sts = boto3.client("sts")
print("IAM identity being used:", sts.get_caller_identity())

# --- Load model from S3 ---
def load_model_from_s3():
    s3 = boto3.client("s3")
    bucket = "realestateforecasting"
    key = "models/price_model.pkl"
    local_model_path = "/tmp/price_model.pkl"

    try:
        if not Path(local_model_path).exists():
            s3.download_file(bucket, key, local_model_path)
    except Exception as e:
        print("❌ Error downloading model:", e)
        raise

    return joblib.load(local_model_path)

# ✅ Global model variable (used in predict, updated in retrain)
model = load_model_from_s3()

# --- Input schema for predictions ---
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

# --- Retrain endpoint ---
@app.post("/retrain")
def retrain_model():
    try:
        # Step 1: Load data from S3
        s3_path = f"s3://{S3_BUCKET}/{S3_DATA_KEY}"
        df = pd.read_csv(s3_path)

        # Step 2: Prep features
        X = df.drop(columns=["price"])
        y = df["price"]

        numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categorical_features = X.select_dtypes(include=["object", "bool"]).columns.tolist()

        preprocessor = ColumnTransformer([
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ])

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", LinearRegression())
        ])

        # Step 3: Train
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        pipeline.fit(X_train, y_train)

        # Step 4: Save locally
        joblib.dump(pipeline, LOCAL_MODEL_PATH)

        # Step 5: Upload back to S3
        s3 = boto3.client("s3")
        s3.upload_file(LOCAL_MODEL_PATH, S3_BUCKET, S3_MODEL_KEY)

        return {"message": "✅ Model retrained and uploaded to S3."}

    except Exception as e:
        return {"error": str(e)}
# --- Health check ---
@app.get("/health")
def health_check():
    return {"status": "ok"}
