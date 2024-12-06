import laspy
import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

# File paths
las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"
output_tif_path = r'C:\Users\User\Documents\azhar_local_code\ikeja\tiff\subset_dem.tif'
output_png_path = r'C:\Users\User\Documents\azhar_local_code\ikeja\projects\png\subset_dem.png'

# Subset settings
subset_points = 30_000_000  # Number of points to process
subset_grid = (600, 400)  # Output DEM dimensions (width x height)
res = 1  # 1-meter resolution

# Load LAS file metadata
with laspy.open(las_file_path) as las:
    x_min, x_max = las.header.mins[0], las.header.maxs[0]
    y_min, y_max = las.header.mins[1], las.header.maxs[1]

# Select a bounding box for the subset
bbox_x_min = x_min + (x_max - x_min) * 0.25  # Adjust as needed
bbox_x_max = bbox_x_min + res * subset_grid[0]
bbox_y_min = y_min + (y_max - y_min) * 0.25  # Adjust as needed
bbox_y_max = bbox_y_min + res * subset_grid[1]

# Collect points within the bounding box
points_x, points_y, points_z = [], [], []
with laspy.open(las_file_path) as las:
    for points in las.chunk_iterator(10_000_000):  # Process in chunks
        mask = (
            (points.x >= bbox_x_min) & (points.x < bbox_x_max) &
            (points.y >= bbox_y_min) & (points.y < bbox_y_max)
        )
        points_x.append(points.x[mask])
        points_y.append(points.y[mask])
        points_z.append(points.z[mask])
        if len(np.hstack(points_x)) >= subset_points:
            break

# Combine points
points_x = np.hstack(points_x)
points_y = np.hstack(points_y)
points_z = np.hstack(points_z)

# Create grid for interpolation
grid_x, grid_y = np.meshgrid(
    np.linspace(bbox_x_min, bbox_x_max, subset_grid[0]),
    np.linspace(bbox_y_min, bbox_y_max, subset_grid[1])
)

# Interpolate the elevation data
dem = griddata(
    points=np.column_stack((points_x, points_y)),
    values=points_z,
    xi=(grid_x, grid_y),
    method='linear'
)

# Fill NaN values with the minimum elevation or 0
dem = np.nan_to_num(dem, nan=np.nanmin(dem))

# Apply affine transformation for georeferencing
transform = Affine.translation(bbox_x_min - res / 2, bbox_y_min - res / 2) * Affine.scale(res, res)
crs = CRS.from_epsg(32735)

# Save the DEM as a GeoTIFF
with rasterio.open(
    output_tif_path, 'w',
    driver='GTiff',
    height=dem.shape[0],
    width=dem.shape[1],
    count=1,
    dtype='float32',
    crs=crs,
    transform=transform
) as out_image:
    out_image.write(dem, 1)

print(f"Subset DEM saved to {output_tif_path}")

# Visualize the DEM with Matplotlib
plt.figure(figsize=(10, 10))
plt.imshow(dem, cmap='gist_earth', origin='lower')
plt.colorbar(label='Elevation (m)')
plt.title('Subset Digital Elevation Model', fontweight='bold')
plt.xlabel("X coords")
plt.ylabel("Y coords")
plt.savefig(output_png_path)
plt.show()

print(f"Subset DEM visualization saved to {output_png_path}")
