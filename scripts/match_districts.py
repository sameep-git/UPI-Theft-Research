import pandas as pd
import geopandas as gpd

# Load the master crime data
crime_data_path = 'data/master_district_data_crime.csv'
crime_df = pd.read_csv(crime_data_path)

# Load the shapefile
shapefile_path = 'data/gadm41_IND_2.shp'
gdf = gpd.read_file(shapefile_path)

# Clean/Normalize strings for better matching
crime_df['District_Clean'] = crime_df['District'].str.strip().str.lower()
crime_df['State_Clean'] = crime_df['State'].str.strip().str.lower()

gdf['District_Clean'] = gdf['NAME_2'].str.strip().str.lower()
gdf['State_Clean'] = gdf['NAME_1'].str.strip().str.lower()

# Basic mapping check
merged = pd.merge(
    crime_df, 
    gdf[['NAME_1', 'NAME_2', 'HASC_2', 'State_Clean', 'District_Clean']], 
    left_on=['State_Clean', 'District_Clean'], 
    right_on=['State_Clean', 'District_Clean'], 
    how='left'
)

# Identify matches and mismatches
matches = merged[merged['HASC_2'].notna()]
mismatches = merged[merged['HASC_2'].isna()]

print(f"Total rows in crime data: {len(crime_df)}")
print(f"Matches found: {len(matches)}")
print(f"Mismatches: {len(mismatches)}")

if len(mismatches) > 0:
    print("\nSample Mismatches (first 20):")
    print(mismatches[['State', 'District']].head(20))

# Save the matched data to a new file, including the HASC code
output_path = 'data/master_district_data_crime_with_codes.csv'
merged.drop(columns=['State_Clean', 'District_Clean', 'NAME_1', 'NAME_2'], inplace=True)
merged.to_csv(output_path, index=False)
print(f"\nSaved matched data to {output_path}")
