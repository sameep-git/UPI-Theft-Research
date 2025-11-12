from pathlib import Path
import importlib.util
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# Paths to the input GeoJSON
india_states_gjson = 'data/INDIA_STATES.geojson'

# Create the output directory if it doesn't exist
output_dir = Path('maps/summ_stats')
output_dir.mkdir(parents=True, exist_ok=True)

# Try to import the new OOP utils class
try:
    from src.utils.utils import GeoUtils
except Exception:
    # fallback: import module from file path
    utils_path = Path(__file__).parent / "utils" / "utils.py"
    spec = importlib.util.spec_from_file_location("utils_module", str(utils_path))
    utils_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utils_module)
    GeoUtils = getattr(utils_module, "GeoUtils")


def generate_summary_stat_heatmap(column_name, vmin=None, vmax=None):
    """
    Generate a state-level heatmap for a specific column from Summary_Stats_Data.csv
    Args:
        column_name (str): Column name from the CSV to visualize
        vmin (float): Minimum value for color scale normalization
        vmax (float): Maximum value for color scale normalization
    """
    # Read the GeoJSON for states
    india_states = gpd.read_file(india_states_gjson)
    
    # Read the summary statistics data
    summary_data = pd.read_csv('data/Summary_Stats_Data.csv')
    
    # Clean state names/codes for merging
    summary_data['State'] = summary_data['State'].str.strip()
    
    # Merge the GeoDataFrame with the summary data
    merged_data = india_states.merge(
        summary_data[['State', column_name]], 
        left_on='STNAME_SH',  # Adjust this based on your GeoJSON column name
        right_on='State',
        how='left'
    )
    
    # If vmin/vmax not provided, calculate from the data
    if vmin is None or vmax is None:
        vmin = summary_data[column_name].min()
        vmax = summary_data[column_name].max()
    
    # Create the heatmap
    fig, ax = plt.subplots(1, 1, figsize=(15, 10), facecolor='#F0F0F0')
    ax.set_facecolor('#F0F0F0')
    
    # Plot the choropleth
    merged_data.plot(
        column=column_name,
        ax=ax,
        legend=True,
        legend_kwds={
            'label': f'{column_name}',
            'orientation': 'vertical',
            'shrink': 0.8,
            'pad': 0.02,
            'fraction': 0.046,
            'format': '%.2f'
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
    
    plt.title(f'{column_name} by State', 
              pad=20, 
              fontsize=16, 
              fontweight='bold',
              fontfamily='sans-serif')
    
    plt.figtext(
        0.99, 0.01, 
        'Source: Summary Statistics Data', 
        ha='right', 
        va='bottom',
        fontsize=8,
        style='italic'
    )
    
    plt.tight_layout(pad=1.2)
    
    # Save the plot to maps/summ_stats/ folder
    output_path = output_dir / f'summary_stats_{column_name}.png'
    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches='tight',
        facecolor='#F0F0F0',
        edgecolor='none',
        pad_inches=0.3
    )
    
    print(f"Saved: {output_path}")
    plt.show()


def generate_all_summary_heatmaps():
    """
    Generate heatmaps for all numeric columns in Summary_Stats_Data.csv
    """
    # Read the summary statistics data
    summary_data = pd.read_csv('data/Summary_Stats_Data.csv')
    
    # Get all numeric columns (excluding State column)
    numeric_columns = summary_data.select_dtypes(include=['number']).columns.tolist()
    
    print(f"Found {len(numeric_columns)} numeric columns to visualize:")
    print(numeric_columns)
    
    # Calculate min/max for each column for consistent scaling
    column_scales = {}
    for col in numeric_columns:
        column_scales[col] = {
            'vmin': summary_data[col].min(),
            'vmax': summary_data[col].max()
        }
    
    # Generate heatmap for each column
    for column in numeric_columns:
        print(f"\nGenerating heatmap for: {column}")
        generate_summary_stat_heatmap(
            column, 
            vmin=column_scales[column]['vmin'],
            vmax=column_scales[column]['vmax']
        )
        plt.close()
    
    print(f"\nAll heatmaps saved to: {output_dir}")


if __name__ == "__main__":
    generate_all_summary_heatmaps()