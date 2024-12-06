import laspy
import numpy as np
from scipy.interpolate import griddata
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS

# Open the LAS file
las = laspy.read(r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las")

# Process in chunks
chunk_size = 10_000_000  # Number of points to process at a time
points = np.empty((0, 2))
elevations = np.empty((0,))

for i in range(0, len(las.x), chunk_size):
    # Extract chunks of data
    chunk_x = las.x[i:i + chunk_size]
    chunk_y = las.y[i:i + chunk_size]
    chunk_z = las.z[i:i + chunk_size]

    # Append to full dataset
    points = np.vstack((points, np.column_stack((chunk_x, chunk_y))))
    elevations = np.concatenate((elevations, chunk_z))

# Create DEM as before using griddata
res = 1  # Resolution
x_range = np.arange(points[:, 0].min(), points[:, 0].max() + res, res)
y_range = np.arange(points[:, 1].min(), points[:, 1].max() + res, res)
grid_x, grid_y = np.meshgrid(x_range, y_range)

dem = griddata(points, elevations, (grid_x, grid_y), method='linear')

# Affine transformation
transform = Affine.translation(grid_x[0][0] - res / 2, grid_y[0][0] - res / 2) * Affine.scale(res, res)
crs = CRS.from_epsg(32735)

# Save as GeoTIFF
tif_path = r'C:\Users\User\Documents\azhar_local_code\ikeja\tiff\dem_big.tif'
with rasterio.open(tif_path, 'w', driver='GTiff', height=dem.shape[0], width=dem.shape[1], count=1, dtype=dem.dtype,
                   crs=crs, transform=transform) as out_image:
    out_image.write(dem, 1)
