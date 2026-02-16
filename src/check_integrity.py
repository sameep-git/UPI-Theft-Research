import pandas as pd

def check_data():
    csv_path = 'data/combined_district_data.csv'
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return

    print(f"Total rows: {len(df)}")
    
    # Check for duplicates in District column (exact string match) within State
    # Note: Since we kept 'first' name, if we had "Guntur Urban" and "Guntur Rural", 
    # the result might satisfy unique constraints on 'District' column if it's just "Guntur Urban".
    # But let's check normalized again to be sure.
    
    # We don't have normalized columns in the final CSV.
    # So we check if (State, District) tuples are unique.
    
    duplicates = df[df.duplicated(subset=['State', 'District'], keep=False)]
    if not duplicates.empty:
        print("ALERT: Duplicates found in (State, District) pairs!")
        print(duplicates[['State', 'District']].head())
    else:
        print("No duplicates in (State, District) pairs found. (Unique identifier verified)")

    # Check for potential unmerged artifacts
    potential_artifacts = df[df['District'].str.contains('Urban|Rural', case=False, regex=True)]
    if not potential_artifacts.empty:
        print(f"\nWarning: {len(potential_artifacts)} rows still contain 'Urban' or 'Rural' in the name:")
        print(potential_artifacts[['State', 'District']].head())
    else:
        print("\nNo 'Urban'/'Rural' artifacts found in District names.")
        
    # Check for NaN values in numeric columns
    print("\nMissing values:")
    print(df.isnull().sum())
    
    # print sample
    print("\nSample rows:")
    print(df.sample(5))

if __name__ == "__main__":
    check_data()
