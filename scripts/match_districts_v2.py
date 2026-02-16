import pandas as pd
import geopandas as gpd

print("Starting matching process...", flush=True)

# Load the master crime data
crime_data_path = 'data/master_district_data_crime.csv'
crime_df = pd.read_csv(crime_data_path)
print(f"Loaded {len(crime_df)} rows from crime data", flush=True)

# Load the shapefile
shapefile_path = 'data/gadm41_IND_2.shp'
gdf = gpd.read_file(shapefile_path)
print(f"Loaded {len(gdf)} records from shapefile", flush=True)

# Normalize strings for better matching
# Remove special characters and lowercase
def clean_string(s):
    if not isinstance(s, str): return str(s)
    return ''.join(e for e in s if e.isalnum()).lower()

crime_df['District_Clean'] = crime_df['District'].apply(clean_string)
crime_df['State_Clean'] = crime_df['State'].apply(clean_string)

gdf['District_Clean'] = gdf['NAME_2'].apply(clean_string)
gdf['State_Clean'] = gdf['NAME_1'].apply(clean_string)

# Basic mapping check
merged = pd.merge(
    crime_df, 
    gdf[['HASC_2', 'State_Clean', 'District_Clean']], 
    left_on=['State_Clean', 'District_Clean'], 
    right_on=['State_Clean', 'District_Clean'], 
    how='left'
)

# Identify matches and mismatches
matches = merged[merged['HASC_2'].notna()]
mismatches = merged[merged['HASC_2'].isna()]

print(f"Total rows in crime data: {len(crime_df)}", flush=True)
print(f"Matches found: {len(matches)}", flush=True)
print(f"Mismatches: {len(mismatches)}", flush=True)

if len(mismatches) > 0:
    print("\nSample Mismatches (first 20):", flush=True)
    for index, row in mismatches.head(20).iterrows():
        print(f"{row['State']} - {row['District']}", flush=True)

# Save the matched data to a new file, including the HASC code
output_path = 'data/master_district_data_crime_with_codes.csv'
# Drop the cleaning columns before saving
columns_to_drop = ['State_Clean', 'District_Clean']
# Check if HASC_2 is already in columns before dropping (it is because we merged)
merged.drop(columns=columns_to_drop, inplace=True)

merged.to_csv(output_path, index=False)
print(f"\nSaved matched data to {output_path}", flush=True)
