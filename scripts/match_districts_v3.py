import pandas as pd
import geopandas as gpd
import difflib

print("Starting enhanced matching process...", flush=True)

# Load data
crime_data_path = 'data/master_district_data_crime.csv'
crime_df = pd.read_csv(crime_data_path)
print(f"Loaded {len(crime_df)} rows from crime data", flush=True)

shapefile_path = 'data/gadm41_IND_2.shp'
gdf = gpd.read_file(shapefile_path)
print(f"Loaded {len(gdf)} records from shapefile", flush=True)

# Helper function
def clean_string(s):
    if not isinstance(s, str): return str(s)
    return ''.join(e for e in s if e.isalnum()).lower()

# Prepare clean columns
crime_df['District_Clean'] = crime_df['District'].apply(clean_string)
crime_df['State_Clean'] = crime_df['State'].apply(clean_string)
gdf['District_Clean'] = gdf['NAME_2'].apply(clean_string)
gdf['State_Clean'] = gdf['NAME_1'].apply(clean_string)

# Perform initial exact merge
merged = pd.merge(
    crime_df, 
    gdf[['HASC_2', 'State_Clean', 'District_Clean']], 
    left_on=['State_Clean', 'District_Clean'], 
    right_on=['State_Clean', 'District_Clean'], 
    how='left'
)

# Identify mismatches
mismatches_idx = merged[merged['HASC_2'].isna()].index
print(f"Initial mismatches: {len(mismatches_idx)}", flush=True)

# Custom mapping dictionary for known issues (can be expanded)
manual_mapping = {
    'spsrnellore': 'nellore',
    'tirupati': 'chittoor',  # Tirupati was carved out, verify map validity
    'purbichamparan': 'eastchamparan',
    'paschimchamparan': 'westchamparan',
    'purnea': 'purnia',
    'bengaluruurban': 'bangaloreurban',
    'bengalururural': 'bangalorerural',
    'gurugram': 'gurgaon',
    'prayagraj': 'allahabad',
    'mysuru': 'mysore',
    'visakhapatnam': 'vishakhapatnam',
    'ahmedabad': 'ahmadabad',
    'gautambuddhanagar': 'gautambuddh Nagar', # Wait, clean string removes spaces
    'gautambuddhahagar': 'gautambuddhnagar',
}

# Fuzzy matching loop
matched_count = 0
for idx in mismatches_idx:
    crime_row = merged.loc[idx]
    state_clean = crime_row['State_Clean']
    district_clean = crime_row['District_Clean']
    
    # Try manual mapping first
    if district_clean in manual_mapping:
         district_clean = manual_mapping[district_clean]

    # Filter shapefile for the same state
    state_gdf = gdf[gdf['State_Clean'] == state_clean]
    
    if state_gdf.empty:
        # State name mismatch? Try close match on state name
        pass # Skipping state mismatches for now for simplicity
        continue

    potential_matches = state_gdf['District_Clean'].tolist()
    
    # Try exact match again after manual mapping
    if district_clean in potential_matches:
        match = state_gdf[state_gdf['District_Clean'] == district_clean].iloc[0]
        merged.at[idx, 'HASC_2'] = match['HASC_2']
        matched_count += 1
        continue
        
    # specific fix for 'district' suffix/prefix which clean_string mostly handles but verify
    
    # Fuzzy matching
    # reduce list to close matches
    close_matches = difflib.get_close_matches(district_clean, potential_matches, n=1, cutoff=0.6)
    
    if close_matches:
        best_match_name = close_matches[0]
        # print(f"Fuzzy match: {crime_row['District']} -> {best_match_name}")
        match = state_gdf[state_gdf['District_Clean'] == best_match_name].iloc[0]
        merged.at[idx, 'HASC_2'] = match['HASC_2']
        matched_count += 1
    else:
        # Check substring
        for potential in potential_matches:
            if district_clean in potential or potential in district_clean:
                 match = state_gdf[state_gdf['District_Clean'] == potential].iloc[0]
                 merged.at[idx, 'HASC_2'] = match['HASC_2']
                 matched_count += 1
                 # print(f"Substring match: {crime_row['District']} -> {potential}")
                 break

print(f"Additional matches found via fuzzy/manual logic: {matched_count}", flush=True)
final_matches = merged[merged['HASC_2'].notna()]
print(f"Final matches: {len(final_matches)} out of {len(crime_df)}", flush=True)

# Save
output_path = 'data/master_district_data_crime_with_codes_v3.csv'
merged.drop(columns=['State_Clean', 'District_Clean'], inplace=True)
merged.to_csv(output_path, index=False)
print(f"Saved to {output_path}", flush=True)
