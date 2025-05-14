# test_clean.py

from src.data.transform_housing_data import run_cleaning_pipeline

# Define input and output file paths (relative to root)
input_path = "data/raw/Housing.csv"
output_path = "data/clean/Housing_cleaned.csv"

if __name__ == "__main__":
    run_cleaning_pipeline(input_path, output_path)
