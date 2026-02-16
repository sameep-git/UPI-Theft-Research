import geopandas as gpd
import pandas as pd

# Load the shapefile
shapefile_path = 'data/gadm41_IND_2.shp'
gdf = gpd.read_file(shapefile_path)

# Print columns
print("Columns in shapefile:", gdf.columns.tolist())

# Print a sample of rows with relevant columns
# Assuming 'NAME_2' is district name and 'HASC_2' is the code based on GADM
if 'NAME_2' in gdf.columns and 'HASC_2' in gdf.columns:
    print("\nSample Data (first 10 rows):")
    print(gdf[['NAME_2', 'HASC_2', 'NAME_1']].head(10))
else:
    print("\nCould not find 'NAME_2' or 'HASC_2'. Printing first 2 rows of all columns:")
    print(gdf.head(2))
