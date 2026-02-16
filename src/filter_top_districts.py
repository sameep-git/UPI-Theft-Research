import pandas as pd
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

try:
    from src.merge_data import normalize_district
except ImportError:
    # If running from root, src.merge_data works if src is a package or we add path
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from merge_data import normalize_district

def clean_population(val):
    if isinstance(val, str):
        return int(val.replace(',', ''))
    return val

def main():
    census_path = "data/census2011.csv"
    combined_path = "data/combined_district_data.csv"
    output_path = "data/combined_district_data_top50.csv"

    print("Loading Census Data...")
    census_df = pd.read_csv(census_path)
    
    # Process Population
    census_df['Population_Clean'] = census_df['Population'].apply(clean_population)
    
    # Sort and take top 50
    top_50_census = census_df.sort_values(by='Population_Clean', ascending=False).head(50)
    
    print("\nTop 10 Districts by Population:")
    print(top_50_census[['District', 'Population_Clean']].head(10))
    
    # Normalize Census District Names for matching
    top_50_census['normalized_name'] = top_50_census['District'].apply(normalize_district)
    
    # Manual Fixes for Top 50 district names to match Combined Data
    # Keys are NORMALIZED census names, Values are NORMALIZED combined names
    manual_mappings = {
        "north twenty four parganas": "north 24 parganas",
        "south twenty four parganas": "south 24 parganas",
        "bangalore": "bengaluru",  # Combined has Bengaluru
        "mumbai suburban": "mumbai", # Combined has Mumbai
        "barddhaman": "east bardhaman", # Combined has East Bardhaman. Paschim might be missing.
        "allahabad": "prayagraj", # Renamed
        "paschim medinipur": "west medinipur",
        "hugli": "hooghly",
        "haora": "howrah",
        "belgaum": "belagavi",
        "ahmadnagar": "ahmednagar",
        "rangareddy": "ranga reddy", # Guessing
        "purba medinipur": "east medinipur", # Rank 14/???
        "mahamaya nagar": "hathras", # Possible rename
        "panch mahals": "panchmahal",
        "kheri": "lakhimpur kheri", # Sometimes just Kheri
        "faizabad": "ayodhya",
        "jyotiba phule nagar": "amroha",
        "kanshiramnagar": "kasganj"
    }
    
    def apply_manual_mapping(name):
        return manual_mappings.get(name, name)

    top_50_census['normalized_name'] = top_50_census['normalized_name'].apply(apply_manual_mapping)
    
    # Set of normalized names to keep
    target_districts = set(top_50_census['normalized_name'].unique())
    print(f"\nIdentifying {len(target_districts)} unique districts from top 50 census list.")

    print("\nLoading Combined District Data...")
    if not os.path.exists(combined_path):
        print(f"Error: {combined_path} not found. Please run merge_data.py first.")
        return

    combined_df = pd.read_csv(combined_path)
    
    # Normalize Combined Data District Names
    combined_df['normalized_name'] = combined_df['District'].apply(normalize_district)
    
    # Filter
    filtered_df = combined_df[combined_df['normalized_name'].isin(target_districts)].copy()
    
    # Drop the temporary normalized column
    filtered_df.drop(columns=['normalized_name'], inplace=True)
    
    print(f"\nFiltered data contains {len(filtered_df)} rows (Districts).")
    
    # Check which districts might have been missed (in top 50 census but not in combined)
    found_districts = set(filtered_df['District'].apply(normalize_district))
    missing = target_districts - found_districts
    if missing:
        print(f"\nWarning: {len(missing)} districts from the Top 50 were not found in the combined dataset:")
        # Try to map back to original names for display
        missing_names = top_50_census[top_50_census['normalized_name'].isin(missing)]['District'].tolist()
        print(missing_names)
    else:
        print("\nAll top 50 districts matched!")

    filtered_df.to_csv(output_path, index=False)
    print(f"\nSaved filtered dataset to {output_path}")

if __name__ == "__main__":
    main()
