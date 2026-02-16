import pandas as pd
import geopandas as gpd
import difflib

# 1. Load Data
print("Loading data...", flush=True)
crime_df = pd.read_csv('data/master_district_data_crime.csv')
shp_gdf = gpd.read_file('data/gadm41_IND_2.shp')
html_df = pd.read_csv('data/html_hasc_mapping.csv')

print(f"Crime Data: {len(crime_df)} rows", flush=True)
print(f"Shapefile: {len(shp_gdf)} rows", flush=True)
print(f"HTML Mapping: {len(html_df)} rows", flush=True)

# 2. Cleanup function
def clean_string(s):
    if not isinstance(s, str): return str(s)
    return ''.join(e for e in s if e.isalnum()).lower()

# 3. Preprocess for merging
crime_df['District_Clean'] = crime_df['District'].apply(clean_string)
crime_df['State_Clean'] = crime_df['State'].apply(clean_string)

shp_gdf['District_Clean'] = shp_gdf['NAME_2'].apply(clean_string)
shp_gdf['State_Clean'] = shp_gdf['NAME_1'].apply(clean_string)

html_df['District_Clean'] = html_df['District'].apply(clean_string)

# Create lookup dicts
# Shapefile lookup: (State_Clean, District_Clean) -> HASC_2
shp_lookup = {}
for idx, row in shp_gdf.iterrows():
    key = (row['State_Clean'], row['District_Clean'])
    shp_lookup[key] = row['HASC_2']

# HTML lookup: District_Clean -> HASC
html_lookup = {}
for idx, row in html_df.iterrows():
    html_lookup[row['District_Clean']] = row['HASC']

# Also create a reverse lookup for shapefile HASC to confirm validity
valid_hasc_codes = set(shp_gdf['HASC_2'].dropna().unique())

# Manual fixes (add your previous ones + any obvious new ones)
manual_mapping = {
    'spsrnellore': 'nellore',
    'tirupati': 'chittoor',
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
    'gautambuddhanagar': 'gautambuddh Nagar',
    'gautambuddhahagar': 'gautambuddhnagar',
}

# 4. Matching Logic
results = []
matched_count = 0
sources = []

for idx, row in crime_df.iterrows():
    dist_orig = row['District']
    dist_clean = row['District_Clean']
    state_clean = row['State_Clean']
    
    # Try manual mapping
    if dist_clean in manual_mapping:
        dist_clean = manual_mapping[dist_clean]

    # Strategy 1: Exact match with Shapefile (State + District)
    hasc = shp_lookup.get((state_clean, dist_clean))
    source = "Shapefile_Exact"
    
    # Strategy 2: HTML Mapping match (District Name only, careful with duplicates)
    if not hasc:
        # Check if the district name exists in HTML mapping
        if dist_clean in html_lookup:
             potential_hasc = html_lookup[dist_clean]
             # VERIFY: Does this HASC exist in our shapefile?
             if potential_hasc in valid_hasc_codes:
                 hasc = potential_hasc
                 source = "HTML_Exact_Verified"
             else:
                 # Code not in shapefile, maybe use it but note it
                 # (for now, let's keep it if we can't find anything else, 
                 # but for plotting it might fail unless we update shapefile too)
                 pass 

    # Strategy 3: Fuzzy match with Shapefile (State restricted)
    if not hasc:
        # Get districts in this state from shapefile
        state_districts = shp_gdf[shp_gdf['State_Clean'] == state_clean]['District_Clean'].tolist()
        matches = difflib.get_close_matches(dist_clean, state_districts, n=1, cutoff=0.7)
        if matches:
            best_match = matches[0]
            hasc = shp_lookup.get((state_clean, best_match))
            source = f"Shapefile_Fuzzy_{best_match}"

    # Record result
    if hasc:
        matched_count += 1
    else:
        source = "Unmatched"
        
    results.append(hasc)
    sources.append(source)

# 5. Save Results
crime_df['HASC_2'] = results
crime_df['Match_Source'] = sources

output_path = 'data/master_district_data_crime_mapped_v2.csv'
crime_df.drop(columns=['District_Clean', 'State_Clean'], inplace=True)
crime_df.to_csv(output_path, index=False)

print(f"Matching complete.", flush=True)
print(f"Total Rows: {len(crime_df)}", flush=True)
print(f"Matched: {matched_count}", flush=True)
print(f"Unmatched: {len(crime_df) - matched_count}", flush=True)

# Breakdown by source
print("\nMatch Sources:", flush=True)
print(pd.Series(sources).value_counts(), flush=True)

# List remaining mismatches
mismatches = crime_df[crime_df['HASC_2'].isna()]
if not mismatches.empty:
    print("\nRemaining Mismatches (Sample):", flush=True)
    print(mismatches[['State', 'District']].head(20).to_string(index=False), flush=True)
