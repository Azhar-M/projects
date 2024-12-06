import laspy
import numpy as np
import rasterio
from rasterio.transform import from_bounds
import matplotlib.pyplot as plt

# File paths
las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"
output_tif_path = r"C:\Users\User\Documents\azhar_local_code\ikeja\tiff\dem_rasterized.tif"
output_png_path = r"C:\Users\User\Documents\azhar_local_code\ikeja\projects\png\big_dem.png"

# Load LAS file
with laspy.open(las_file_path) as las:
    # Get bounds of the LAS file
    x_min, x_max = las.header.mins[0], las.header.maxs[0]
    y_min, y_max = las.header.mins[1], las.header.maxs[1]

    # Resolution
    res = 1  # 1-meter resolution

    # Create the raster dimensions
    width = int((x_max - x_min) / res)
    height = int((y_max - y_min) / res)

    # Define the transformation matrix
    transform = from_bounds(x_min, y_min, x_max, y_max, width, height)

    # Initialize an empty raster array
    raster = np.zeros((height, width), dtype=np.float32)

    # Process in chunks
    chunk_size = 10_000_000  # Number of points per chunk
    for points in las.chunk_iterator(chunk_size):
        # Extract X, Y, Z values
        x = points.x
        y = points.y
        z = points.z

        # Convert points to pixel indices
        row = ((y_max - y) / res).astype(int)
        col = ((x - x_min) / res).astype(int)

        # Update raster values (use max elevation per pixel for simplicity)
        for r, c, value in zip(row, col, z):
            if 0 <= r < height and 0 <= c < width:  # Ensure within bounds
                raster[r, c] = max(raster[r, c], value)

# Visualize the raster
plt.figure(figsize=(10, 10))
plt.imshow(raster, cmap='gist_earth', origin='lower')
plt.colorbar(label='Elevation (m)')
plt.title('Digital Elevation Model', fontweight='bold')
plt.xlabel("X coords")
plt.ylabel("Y coords")
plt.savefig(output_png_path)
plt.show()

# Write the raster to a GeoTIFF file
with rasterio.open(
    output_tif_path,
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype=raster.dtype,
    crs="EPSG:32735",
    transform=transform
) as dst:
    dst.write(raster, 1)

print(f"Raster DEM saved to {output_tif_path}")
print(f"Raster visualization saved to {output_png_path}")
