import geopandas as gpd
from pathlib import Path


class GeoUtils:
    """Small collection of geospatial utility methods.

    Usage:
        GeoUtils.convert_geojson_to_shp('in.geojson', 'out.shp')
    """

    @staticmethod
    def convert_geojson_to_shp(input_path, output_path):
        """Read a GeoJSON and write it out as a Shapefile.

        Args:
            input_path: Path-like or string pointing to the .geojson file.
            output_path: Path-like or string where the .shp (and related files)
                will be written.
        """
        geo_df = gpd.read_file(str(input_path))
        geo_df.to_file(str(output_path))


# Backwards-compatible module-level function
def convert_geojson_to_shp(input_path, output_path):
    return GeoUtils.convert_geojson_to_shp(input_path, output_path)
