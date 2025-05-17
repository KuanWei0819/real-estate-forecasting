from src.model.train_model import train_model

input_path = "data/clean/Housing_cleaned.csv"
output_path = "models/housing_price_model.pkl"

if __name__ == "__main__":
    train_model(input_path, output_path)
