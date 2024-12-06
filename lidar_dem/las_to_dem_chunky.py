import laspy
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

# File paths
las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"
output_tif_path = r"C:\Users\User\Documents\azhar_local_code\ikeja\tiff\chunked_dem.tif"
output_png_path = r"C:\Users\User\Documents\azhar_local_code\ikeja\projects\png\big_dem.png"

# Load LAS metadata to get bounds
with laspy.open(las_file_path) as las:
    x_min, x_max = las.header.mins[0], las.header.maxs[0]
    y_min, y_max = las.header.mins[1], las.header.maxs[1]

# Define grid resolution and dimensions
res = 5  # 2-meter resolution
width = int((x_max - x_min) / res)
height = int((y_max - y_min) / res)

# Create a grid canvas with NaN values (empty DEM)
dem_grid = np.full((height, width), np.nan, dtype=np.float32)

# Transformation and CRS
transform = from_bounds(x_min, y_min, x_max, y_max, width, height)
crs = CRS.from_epsg(32735)

# Generate grid coordinates that perfectly match the DEM grid
grid_x, grid_y = np.meshgrid(
    np.linspace(x_min, x_max, width),  # Exact alignment with bounds and resolution
    np.linspace(y_min, y_max, height)
)

# Define chunking parameters
chunk_size = 10_000_000  # Points per chunk
buffer = 10  # Add 10 meters of overlap between chunks

# Processing LAS file in chunks
chunk_num = 0
with laspy.open(las_file_path) as las:
    for points in las.chunk_iterator(chunk_size):
        x = points.x
        y = points.y
        z = points.z

        # Compute bounds for the current chunk with buffer
        chunk_x_min = max(x.min() - buffer, x_min)
        chunk_x_max = min(x.max() + buffer, x_max)
        chunk_y_min = max(y.min() - buffer, y_min)
        chunk_y_max = min(y.max() + buffer, y_max)

        # Generate grid for the current chunk
        chunk_grid_x, chunk_grid_y = np.meshgrid(
            np.linspace(chunk_x_min, chunk_x_max, int((chunk_x_max - chunk_x_min) / res)),
            np.linspace(chunk_y_min, chunk_y_max, int((chunk_y_max - chunk_y_min) / res))
        )

        # Interpolate the chunk's elevation data
        dem_chunk = griddata(
            points=np.column_stack((x, y)),
            values=z,
            xi=(chunk_grid_x, chunk_grid_y),
            method='linear',
        )

        # Fill NaN values in dem_chunk with nearest interpolation
        if np.any(np.isnan(dem_chunk)):
            nearest_chunk = griddata(
                points=np.column_stack((x, y)),
                values=z,
                xi=(chunk_grid_x, chunk_grid_y),
                method='nearest',
            )
            dem_chunk[np.isnan(dem_chunk)] = nearest_chunk[np.isnan(dem_chunk)]

        # Calculate the row and column indices in the global DEM grid
        row_start = int((chunk_y_min - y_min) / res)
        row_end = row_start + dem_chunk.shape[0]
        col_start = int((chunk_x_min - x_min) / res)
        col_end = col_start + dem_chunk.shape[1]

        # Merge the chunk data into the global DEM grid
        dem_grid[row_start:row_end, col_start:col_end] = np.fmax(
            dem_grid[row_start:row_end, col_start:col_end], dem_chunk
        )

        chunk_num += 1
        print(f"Processed chunk {chunk_num}")

# Apply smoothing to reduce artifacts
dem_grid = gaussian_filter(dem_grid, sigma=2)

# Replace NaN values with the grid's minimum elevation
dem_grid = np.nan_to_num(dem_grid, nan=np.nanmin(dem_grid))

# Write the DEM grid to a GeoTIFF file
with rasterio.open(
    output_tif_path,
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype=dem_grid.dtype,
    crs=crs,
    transform=transform
) as dst:
    dst.write(dem_grid, 1)

print(f"Chunked DEM saved to {output_tif_path}")

# Visualize the DEM with Matplotlib
plt.figure(figsize=(10, 10))
plt.imshow(dem_grid, cmap='gist_earth', origin='lower')
plt.colorbar(label='Elevation (m)')
plt.title('Digital Elevation Model', fontweight='bold')
plt.savefig(output_png_path)
plt.show()

print(f"DEM visualization saved to {output_png_path}")



# # File paths
# las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"
# output_tif_path = r"C:\Users\User\Documents\azhar_local_code\ikeja\tiff\chunked_dem.tif"
# output_png_path = r"C:\Users\User\Documents\azhar_local_code\ikeja\projects\png\big_dem.png"

# # Load LAS metadata to get bounds
# with laspy.open(las_file_path) as las:
#     x_min, x_max = las.header.mins[0], las.header.maxs[0]
#     y_min, y_max = las.header.mins[1], las.header.maxs[1]

# # Define grid resolution and dimensions
# res = 1  # 1-meter resolution
# width = int((x_max - x_min) / res)
# height = int((y_max - y_min) / res)

# # Create a grid canvas with NaN values (empty DEM)
# dem_grid = np.full((height, width), np.nan, dtype=np.float32)

# # Transformation and CRS
# transform = from_bounds(x_min, y_min, x_max, y_max, width, height)
# crs = CRS.from_epsg(32735)

# # Generate grid coordinates that perfectly match the DEM grid
# grid_x, grid_y = np.meshgrid(
#     np.linspace(x_min, x_max, width),  # Exact alignment with bounds and resolution
#     np.linspace(y_min, y_max, height)
# )


# # Process LAS file in chunks
# chunk_size = 10_000_000  # Points per chunk
# chunk_num = 0
# with laspy.open(las_file_path) as las:
#     for points in las.chunk_iterator(chunk_size):
#         # Extract x, y, z coordinates from the chunk
#         x = points.x
#         y = points.y
#         z = points.z

#         # Interpolate the chunk's elevation data onto the DEM grid
#         dem_chunk = griddata(
#             points=np.column_stack((x, y)),
#             values=z,
#             xi=(grid_x, grid_y),
#             method='linear',
#         )

#         # Fill NaN values in dem_chunk with nearest interpolation
#         if np.any(np.isnan(dem_chunk)):
#             dem_chunk[np.isnan(dem_chunk)] = griddata(
#                 points=np.column_stack((x, y)),
#                 values=z,
#                 xi=(grid_x, grid_y),
#                 method='nearest',
#             )[np.isnan(dem_chunk)]

#         # Update the global DEM grid with the chunk's data
#         dem_grid = np.fmax(dem_grid, dem_chunk)
#         chunk_num += 1
#         print(f"Processed chunk {chunk_num}")

# # Replace any remaining NaN values with 0
# dem_grid = np.nan_to_num(dem_grid, nan=0)

# # Write the DEM grid to a GeoTIFF file
# with rasterio.open(
#     output_tif_path,
#     'w',
#     driver='GTiff',
#     height=height,
#     width=width,
#     count=1,
#     dtype=dem_grid.dtype,
#     crs=crs,
#     transform=transform
# ) as dst:
#     dst.write(dem_grid, 1)

# print(f"Chunked DEM saved to {output_tif_path}")

# # Visualize the DEM with Matplotlib
# plt.figure(figsize=(10, 10))
# plt.imshow(dem_grid, cmap='gist_earth', origin='lower')
# plt.colorbar(label='Elevation (m)')
# plt.title('Digital Elevation Model', fontweight='bold')
# plt.xlabel("X coords")
# plt.ylabel("Y coords")
# plt.savefig(output_png_path)
# # plt.show()

# print(f"DEM visualization saved to {output_png_path}")
