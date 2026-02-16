import pandas as pd
import re

def clean_column_name(col):
    col = col.lower()
    col = re.sub(r'[^a-z0-9_]', '_', col)
    if not col[0].isalpha() and col[0] != '_':
        col = '_' + col
    return col

def main():
    input_path = 'data/combined_district_data.csv'
    output_dta_path = 'data/combined_district_data.dta'
    output_csv_path = 'data/combined_district_data_stata.csv'

    print("Loading data...")
    df = pd.read_csv(input_path)

    # Clean column names
    df.columns = [clean_column_name(c) for c in df.columns]

    # Ensure numeric columns
    numeric_cols = [c for c in df.columns if 'theft' in c or 'registered' in c]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Ensure strings
    text_cols = ['state', 'district']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Save to DTA
    try:
        df.to_stata(output_dta_path, version=118, write_index=False)
        print(f"Successfully saved Stata file: {output_dta_path}")
    except Exception as e:
        print(f"Error saving .dta file: {e}")

    # Save Clean CSV
    df.to_csv(output_csv_path, index=False)
    print(f"Successfully saved clean CSV: {output_csv_path}")

if __name__ == "__main__":
    main()
