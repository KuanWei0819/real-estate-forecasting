import pandas as pd
from pathlib import Path

def clean_housing_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning of the raw housing dataset.
    - Strips and lowers string columns
    - Removes leading/trailing whitespace
    - Drops duplicate rows (if any)
    """
    df_clean = df.copy()

    # Standardize object columns
    for col in df_clean.select_dtypes(include="object").columns:
        df_clean[col] = df_clean[col].str.strip().str.lower()

    # Drop duplicates (if any)
    df_clean = df_clean.drop_duplicates()

    return df_clean

def run_cleaning_pipeline(input_path: str, output_path: str):
    """
    Load raw CSV, clean it, and save to new CSV
    """
    # Load raw data
    df = pd.read_csv(input_path)

    # Clean it
    df_clean = clean_housing_data(df)

    # Ensure output folder exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Save cleaned file
    df_clean.to_csv(output_path, index=False)

    print(f"✅ Cleaned data saved to: {output_path}")
