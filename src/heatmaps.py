from pathlib import Path
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# Paths to the input GeoJSON and output Shapefile
india_districts_gjson = 'data/INDIA_DISTRICTS.geojson'
india_districts_shp = 'data/gadm41_IND_2.shp'

# Try to import the new OOP utils class. If running this file directly as a
# script (rather than as a module), the package import may fail; in that case
# fall back to loading the utils module by path.
try:
	from src.utils.utils import GeoUtils
except Exception:
	# fallback: import module from file path
	import importlib.util
	utils_path = Path(__file__).parent / "utils" / "utils.py"
	spec = importlib.util.spec_from_file_location("utils_module", str(utils_path))
	utils_module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(utils_module)
	GeoUtils = getattr(utils_module, "GeoUtils")


def ensure_shapefile():
	"""Ensure the districts shapefile exists; convert from geojson if needed."""
	shp_path = Path(india_districts_shp)
	if not shp_path.exists():
		print(f"{shp_path} not found — converting from {india_districts_gjson}...")
		GeoUtils.convert_geojson_to_shp(india_districts_gjson, india_districts_shp)
		print("Conversion complete.")
	else:
		print(f"{shp_path} already exists.")

def generate_theft_heatmap(year, vmin=None, vmax=None):
    """
    Generate a theft rate heatmap for a specific year
    Args:
        year (int): Year for which to generate the heatmap (e.g., 2017, 2018, 2019)
        vmin (float): Minimum value for color scale normalization
        vmax (float): Maximum value for color scale normalization
    """
    # Read the shapefile and main data
    india_districts = gpd.read_file(india_districts_shp)
    main_data = pd.read_csv('data/main_data.csv')
    
    # Clean the district codes (remove any whitespace)
    main_data['District_Code'] = main_data['District_Code'].str.strip()
    main_data['District_Code'] = main_data['District_Code'].str.split(',')
    
    # Column name for the specific year
    theft_rate_col = f'Theft_Rate_{year}'
    
    # If vmin/vmax not provided, calculate from all years
    if vmin is None or vmax is None:
        all_years_data = pd.read_csv('data/main_data.csv')
        theft_rates = []
        for yr in [2017, 2018, 2019]:
            year_rate = all_years_data[f'Theft_Rate_{yr}']
            theft_rates.extend(year_rate)
        vmin = min(theft_rates)
        vmax = max(theft_rates)
    
    # Explode and clean the individual district codes
    main_data_exploded = main_data.explode('District_Code')
    main_data_exploded['District_Code'] = main_data_exploded['District_Code'].str.strip()
    
    # Merge the GeoDataFrame with the main data
    merged_data = india_districts.merge(
        main_data_exploded[['District_Code', theft_rate_col]], 
        left_on='HASC_2',
        right_on='District_Code',
        how='left'
    )
    
    # Print merge results
    successful_matches = merged_data[merged_data[theft_rate_col].notna()]
    print(f"\nSuccessful matches for {year}:")
    print(successful_matches[['HASC_2', 'District_Code', theft_rate_col]])
    
    # Create the heatmap with a specific figure size and background color
    fig, ax = plt.subplots(1, 1, figsize=(15, 10), facecolor='#F0F0F0')
    ax.set_facecolor('#F0F0F0')
    
    # Plot the choropleth with enhanced colors and borders
    merged_data.plot(
        column=theft_rate_col,
        ax=ax,
        legend=True,
        legend_kwds={
            'label': f'Theft Rate per 100,000 People\n({year})',
            'orientation': 'vertical',
            'shrink': 0.8,
            'pad': 0.02,
            'fraction': 0.046,
            'format': '%.1f'
        },
        missing_kwds={'color': '#E6E6E6', 'label': 'No Data'},
        cmap='RdYlBu_r',
        edgecolor='#404040',
        linewidth=0.3,
        vmin=vmin,
        vmax=vmax
    )
    
    # Add country outline with a more distinct border
    merged_data.boundary.plot(
        ax=ax,
        edgecolor='#202020',
        linewidth=1.0
    )
    
    ax.axis('off')
    
    plt.title(f'Theft Rate in India by District ({year})', 
              pad=20, 
              fontsize=16, 
              fontweight='bold',
              fontfamily='sans-serif')
    
    plt.figtext(
        0.99, 0.01, 
        f'Source: Crime in India {year}', 
        ha='right', 
        va='bottom',
        fontsize=8,
        style='italic'
    )
    
    plt.tight_layout(pad=1.2)
    
    plt.savefig(
        f'maps/heatmaps/theft_heatmap_{year}.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='#F0F0F0',
        edgecolor='none',
        pad_inches=0.3
    )
    
    plt.show()

def generate_adoption_heatmap(year, vmin=None, vmax=None):
    """
    Generate a UPI user adoption rate heatmap for a specific year
    Args:
        year (int): Year for which to generate the heatmap (e.g., 2018, 2019, 2020)
        vmin (float): Minimum value for color scale normalization
        vmax (float): Maximum value for color scale normalization
    """
    # Read the shapefile and main data
    india_districts = gpd.read_file(india_districts_shp)
    main_data = pd.read_csv('data/main_data.csv')
    
    # Clean the district codes
    main_data['District_Code'] = main_data['District_Code'].str.strip()
    main_data['District_Code'] = main_data['District_Code'].str.split(',')
    
    # Calculate adoption rate before exploding
    users_col = f'Users_{year}'
    main_data['Adoption_Rate'] = (main_data[users_col] / main_data['Population_2011']) * 100
    
    # Explode and clean the individual district codes
    main_data_exploded = main_data.explode('District_Code')
    main_data_exploded['District_Code'] = main_data_exploded['District_Code'].str.strip()
    
    # Merge the GeoDataFrame with the main data
    merged_data = india_districts.merge(
        main_data_exploded[['District_Code', 'Adoption_Rate']], 
        left_on='HASC_2',
        right_on='District_Code',
        how='left'
    )

    # If vmin/vmax not provided, calculate from all years
    if vmin is None or vmax is None:
        all_years_data = pd.read_csv('data/main_data.csv')
        adoption_rates = []
        for yr in [2018, 2019, 2020]:
            users_col = f'Users_{yr}'
            year_rate = (all_years_data[users_col] / all_years_data['Population_2011']) * 100
            adoption_rates.extend(year_rate)
        vmin = min(adoption_rates)
        vmax = max(adoption_rates)

    # Create the heatmap
    fig, ax = plt.subplots(1, 1, figsize=(15, 10), facecolor='#F0F0F0')
    ax.set_facecolor('#F0F0F0')
    
    # Plot the choropleth with consistent color scale
    merged_data.plot(
        column='Adoption_Rate',
        ax=ax,
        legend=True,
        legend_kwds={
            'label': f'UPI Adoption Rate (%)\n({year})',
            'orientation': 'vertical',
            'shrink': 0.8,
            'pad': 0.02,
            'fraction': 0.046,
            'format': '%.1f%%'
        },
        missing_kwds={'color': '#E6E6E6', 'label': 'No Data'},
        cmap='viridis',
        edgecolor='#404040',
        linewidth=0.3,
        vmin=vmin,
        vmax=vmax
    )
    
    # Add country outline
    merged_data.boundary.plot(
        ax=ax,
        edgecolor='#202020',
        linewidth=1.0
    )
    
    ax.axis('off')
    
    plt.title(f'UPI User Adoption Rate by District ({year})', 
              pad=20, 
              fontsize=16, 
              fontweight='bold',
              fontfamily='sans-serif')
    
    plt.figtext(
        0.99, 0.01, 
        f'Source: UPI Transaction Data {year}\nPopulation based on Census 2011', 
        ha='right', 
        va='bottom',
        fontsize=8,
        style='italic'
    )
    
    plt.tight_layout(pad=1.2)
    
    plt.savefig(
        f'maps/heatmaps/adoption_heatmap_{year}.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='#F0F0F0',
        edgecolor='none',
        pad_inches=0.3
    )
    
    plt.show()

# Update main to generate maps for all years
if __name__ == "__main__":
    ensure_shapefile()
    
    # Calculate min/max theft rates across all years
    main_data = pd.read_csv('data/main_data.csv')
    theft_rates = []
    for year in [2017, 2018, 2019]:
        theft_rates.extend(main_data[f'Theft_Rate_{year}'])
    theft_vmin = min(theft_rates)
    theft_vmax = max(theft_rates)
    
    # Calculate min/max adoption rates across all years
    adoption_rates = []
    for year in [2018, 2019, 2020]:
        users_col = f'Users_{year}'
        year_rate = (main_data[users_col] / main_data['Population_2011']) * 100
        adoption_rates.extend(year_rate)
    adoption_vmin = min(adoption_rates)
    adoption_vmax = max(adoption_rates)
    
    # Generate theft heatmaps with consistent scale
    for year in [2017, 2018, 2019]:
        generate_theft_heatmap(year, vmin=theft_vmin, vmax=theft_vmax)
        plt.close()
    
    # Generate adoption heatmaps with consistent scale
    for year in [2018, 2019, 2020]:
        generate_adoption_heatmap(year, vmin=adoption_vmin, vmax=adoption_vmax)
        plt.close()
