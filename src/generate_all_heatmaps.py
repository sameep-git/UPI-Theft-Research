import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re

# Configuration
input_data_path = 'data/master_district_data_crime_mapped_v2.csv'
shapefile_path = 'data/gadm41_IND_2.shp'
output_dir = Path('maps/heatmaps')
output_dir.mkdir(parents=True, exist_ok=True)

def generate_all_heatmaps():
    print("Loading data...", flush=True)
    # Load data
    df = pd.read_csv(input_data_path)
    # Ensure HASC_2 is string to match shapefile
    df['HASC_2'] = df['HASC_2'].astype(str)

    print("Aggregating duplicates (summing values for same HASC code)...", flush=True)
    # Group by HASC_2 and sum
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    df_agg = df.groupby('HASC_2', as_index=False)[numeric_cols].sum()

    print("Loading shapefile...", flush=True)
    gdf = gpd.read_file(shapefile_path)
    
    # Merge upfront - we'll use this merged gdf for all plots
    # Keep left to preserve all geometry even if no data match
    merged_gdf = gdf.merge(df_agg, on='HASC_2', how='left')

    # Identify all value columns (Variable_Year)
    # We look for columns ending in _YYYY
    value_cols = [col for col in df_agg.columns if re.search(r'_\d{4}$', col)]
    
    if not value_cols:
        print("No columns matching pattern 'Variable_Year' found.", flush=True)
        return

    print(f"Found {len(value_cols)} variable-year columns to plot.", flush=True)

    # Calculate global min/max for each variable type across all years
    variable_ranges = {}
    for col in value_cols:
        parts = col.rsplit('_', 1)
        variable_name = parts[0]
        
        # Get data for this column
        col_data = merged_gdf[col].dropna()
        if col_data.empty:
            continue
            
        col_min = col_data.min()
        col_max = col_data.max()
        
        if variable_name not in variable_ranges:
            variable_ranges[variable_name] = {'min': col_min, 'max': col_max}
        else:
            variable_ranges[variable_name]['min'] = min(variable_ranges[variable_name]['min'], col_min)
            variable_ranges[variable_name]['max'] = max(variable_ranges[variable_name]['max'], col_max)

    print("Calculated global ranges for variables:")
    for var, limits in variable_ranges.items():
        print(f"  {var}: {limits['min']} - {limits['max']}")

    for col in value_cols:
        print(f"Generating heatmap for {col}...", flush=True)
        
        # Parse variable and year for title
        parts = col.rsplit('_', 1)
        variable_name = parts[0]
        year = parts[1]
        
        # Get ranges
        vmin = variable_ranges.get(variable_name, {}).get('min')
        vmax = variable_ranges.get(variable_name, {}).get('max')
        
        # Create plot
        fig, ax = plt.subplots(1, 1, figsize=(15, 12))
        
        # Plot base map (grey for missing data)
        merged_gdf.plot(ax=ax, color='#f0f0f0', edgecolor='white', linewidth=0.2)
        
        # Plot data
        # Check if column has any valid data
        if merged_gdf[col].notna().any():
            merged_gdf.plot(
                column=col,
                ax=ax,
                legend=True,
                legend_kwds={'label': f"{variable_name} ({year})", 'orientation': "vertical", 'shrink': 0.7},
                cmap='YlOrRd', # Yellow-Orange-Red implies intensity
                missing_kwds={'color': 'lightgrey', 'label': 'Missing values'},
                edgecolor='black',
                linewidth=0.1,
                vmin=vmin,
                vmax=vmax
            )
            
            ax.set_title(f"{variable_name} across Districts - {year}", fontsize=16)
            ax.set_axis_off()
            
            output_filename = output_dir / f"{variable_name}_{year}.png"
            plt.savefig(output_filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Saved {output_filename}")
        else:
            print(f"Skipping {col} - no data available.")
            plt.close(fig)

if __name__ == "__main__":
    generate_all_heatmaps()
