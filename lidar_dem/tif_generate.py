import numpy as np
import rasterio
from rasterio.transform import from_origin

# Create a sample DEM array (10x10 grid with elevation values)
# dem_array = np.array([
#     [0, 0, 0, 0, 5, 0, 0, 10, 15, 0],
#     [10, 10, 0, 0, 0, 5, 5, 10, 10, 0],
#     [10, 15, 10, 10, 0, 8, 5, 0, 0, 0],
#     [0, 10, 0, 5, 0, 0, 10, 10, 15, 15],
#     [10, 0, 5, 15, 10, 10, 5, 5, 0, 0],
#     [15, 5, 10, 5, 0, 30, 5, 5, 5, 5],  
#     [0, 5, 5, 10, 10, 15, 5, 5, 10, 5],
#     [0, 0, 40, 0, 0, 5, 5, 5, 0, 10],
#     [0, 5, 5, 10, 10, 10, 10, 10, 10, 5],
#     [0, 0, 5, 15, 15, 5, 15, 0, 0, 0]
# ])

dem_array = np.array([
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
    [100, 100, 100, 100, 100, 100, 100, 150, 100, 100],
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
    [100, 100, 100, 111, 100, 110, 100, 100, 100, 100],  # One height is greater
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
])

# Define the transform (top-left corner coordinates, pixel size)
transform = from_origin(0, 10, 1, 1)  # (west, north, xsize, ysize)

# Define the metadata
metadata = {
    'driver': 'GTiff',
    'height': dem_array.shape[0],
    'width': dem_array.shape[1],
    'count': 1,
    'dtype': dem_array.dtype,
    'crs': 'EPSG:4326',  # Coordinate reference system (WGS84)
    'transform': transform
}

# Write the array to a TIFF file
with rasterio.open('sample_dem.tif', 'w', **metadata) as dst:
    dst.write(dem_array, 1)

print("Sample DEM TIFF file created successfully.")


# dem_array = np.array([
#     [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
#     [100, 110, 100, 100, 100, 100, 100, 100, 100, 100],
#     [100, 100, 120, 100, 100, 100, 100, 100, 100, 100],
#     [100, 100, 100, 130, 100, 100, 100, 100, 100, 100],
#     [100, 100, 100, 100, 140, 100, 100, 100, 100, 100],
#     [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],  # One height is greater
#     [100, 100, 100, 100, 100, 100, 160, 100, 100, 100],
#     [100, 100, 100, 100, 100, 100, 100, 170, 100, 100],
#     [100, 100, 100, 100, 100, 100, 100, 100, 180, 100],
#     [100, 100, 100, 100, 100, 100, 100, 100, 100, 190]
# ])