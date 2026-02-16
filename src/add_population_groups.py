import pandas as pd
import sys
import os
import numpy as np

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

try:
    from src.merge_data import normalize_district
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from merge_data import normalize_district

def clean_population(val):
    if isinstance(val, str):
        return int(val.replace(',', ''))
    return val

def get_manual_mappings():
    # Improved mappings
    return {
        "north twenty four parganas": "north 24 parganas",
        "south twenty four parganas": "south 24 parganas",
        "bangalore": "bengaluru",
        "mumbai suburban": "mumbai",
        "barddhaman": "east bardhaman", 
        "allahabad": "prayagraj", 
        "paschim medinipur": "west medinipur",
        "hugli": "hooghly",
        "haora": "howrah",
        "belgaum": "belagavi",
        "ahmadnagar": "ahmednagar",
        "rangareddy": "ranga reddy",
        "purba medinipur": "east medinipur",
        "mahamaya nagar": "hathras",
        "panch mahals": "panchmahal",
        "kheri": "lakhimpur kheri",
        "faizabad": "ayodhya",
        "jyotiba phule nagar": "amroha",
        "kanshiramnagar": "kasganj",
        "sant ravidas nagar": "bhadohi",
        
        # New additions
        "cuddapah": "ysr",
        "y.s.r.": "ysr",
        "sri potti sriramulu nellore": "spsr nellore",
        "nellore": "spsr nellore",
        "mysore": "mysuru",
        "shimoga": "shivamogga",
        "gulbarga": "kalaburagi",
        "bijapur": "vijayapura",
        "bellary": "ballari",
        "chikmagalur": "chikkamagaluru",
        "tumkur": "tumakuru",
        "hubli-dharwad": "dharwad",
        
        # Telangana / AP Split issues
        "warangal": "warangal urban", # Split into Urban/Rural, mapping to Urban usually
        "karimnagar": "karimnagar", 
        
        # Other renames
        "gurgaon": "gurugram",
        "mewat": "nuh",
        "jajpur": "jajapur",
        "nabarangapur": "nabarangpur",
        "subarnapur": "sonepur"
    }

def main():
    census_path = "data/census2011.csv"
    combined_path = "data/combined_district_data.csv"
    output_path = "data/combined_district_data_with_sizes.csv"

    print("Loading Census Data...")
    census_df = pd.read_csv(census_path)
    
    # Process Population
    census_df['Population_Clean'] = census_df['Population'].apply(clean_population)
    
    # Calculate Statistics
    pop_series = census_df['Population_Clean']
    
    # Use percentiles as requested
    # Quartiles: 0-25, 25-50, 50-75, 75-100
    p25 = np.percentile(pop_series, 25)
    p50 = np.percentile(pop_series, 50)
    p75 = np.percentile(pop_series, 75)
    
    print("\n--- Population Statistics (Census 2011) ---")
    print(f"Mean: {pop_series.mean():,.0f}")
    print(f"Median: {p50:,.0f}")
    print(f"25th Percentile: {p25:,.0f}")
    print(f"75th Percentile: {p75:,.0f}")
    
    print(f"\nDefining Size Groups (Quartiles):")
    print(f"Group 1 (Small):        <= {p25:,.0f}")
    print(f"Group 2 (Medium-Small): {p25:,.0f} - {p50:,.0f}")
    print(f"Group 3 (Medium-Large): {p50:,.0f} - {p75:,.0f}")
    print(f"Group 4 (Large):        > {p75:,.0f}")

    # Assign Size Groups
    def assign_group(pop):
        if pop <= p25: return 1
        elif pop <= p50: return 2
        elif pop <= p75: return 3
        else: return 4
        
    census_df['size_group'] = census_df['Population_Clean'].apply(assign_group)
    
    # Check for Srikakulam in Census
    sri_check = census_df[census_df['District'].str.contains('Srikakulam', case=False, na=False)]
    if not sri_check.empty:
        print(f"\nFound Srikakulam in Census: {sri_check['District'].values[0]}")
    else:
        print("\nWARNING: Srikakulam NOT found in Census data.")

    # Prepare for Merge
    census_df['normalized_name'] = census_df['District'].apply(normalize_district)
    
    # Apply manual mappings to census names (Standardize to Combined format)
    mappings = get_manual_mappings()
    census_df['normalized_name'] = census_df['normalized_name'].apply(lambda x: mappings.get(x, x))
    
    # Deduplicate (Census 2011 shouldn't have dups, but safety first)
    census_lookup = census_df.sort_values('Population_Clean', ascending=False).drop_duplicates('normalized_name')
    census_lookup = census_lookup[['normalized_name', 'Population_Clean', 'size_group']]
    census_lookup.rename(columns={'Population_Clean': 'Population_2011'}, inplace=True)

    print("\nLoading Combined District Data to merge...")
    if not os.path.exists(combined_path):
        print(f"Error: {combined_path} not found.")
        return

    combined_df = pd.read_csv(combined_path)
    combined_df['normalized_name_temp'] = combined_df['District'].apply(normalize_district)
    
    # Extra normalization for Combined data to match Mappings keys if needed? 
    # No, mappings map Census -> Combined.
    # But reverse mappings might be needed if Combined has the "Old" name?
    # Actually, normalize_district handles some.
    
    # Merge
    merged_df = pd.merge(combined_df, census_lookup, left_on='normalized_name_temp', right_on='normalized_name', how='left')
    
    # Check Srikakulam again in results
    check_res = merged_df[merged_df['District'] == 'Srikakulam']
    if not check_res.empty:
        print(f"Result for Srikakulam: Match found? {check_res['size_group'].notna().values[0]}")

    # Check match rate
    total = len(combined_df)
    matched = merged_df['size_group'].notna().sum()
    print(f"\nMatch Results:")
    print(f"Total Combined Districts: {total}")
    print(f"Matched with Census Data: {matched} ({matched/total*100:.1f}%)")
    
    missing = merged_df[merged_df['size_group'].isna()]
    if not missing.empty:
        print(f"\nSample of unmatched districts ({len(missing)} total):")
        print(missing['District'].head(20).tolist())
    
    # Clean up columns
    merged_df.drop(columns=['normalized_name', 'normalized_name_temp'], inplace=True)
    
    merged_df.to_csv(output_path, index=False)
    print(f"\nSaved extended dataset with size groups to {output_path}")

if __name__ == "__main__":
    main()
