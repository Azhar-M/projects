import laspy
import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from pyproj import Transformer


# File paths
las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"
output_tif_dir = r'C:\Users\User\Documents\azhar_local_code\ikeja\tiff\chunk_overlap'
output_png_dir = r'C:\Users\User\Documents\azhar_local_code\ikeja\projects\png\chunk_overlap_png'

# Fixed settings
subset_points = 10_000_000  # Number of points to process per tile
res = 1  
overlap  = 50 #50m overlap between tiles
tile_size = 500
grid_size = (tile_size, tile_size)  # Output DEM dimensions (width x height)


# Load LAS file metadata
with laspy.open(las_file_path) as las:
    x_min, x_max = las.header.mins[0], las.header.maxs[0]
    y_min, y_max = las.header.mins[1], las.header.maxs[1]

# # Calculate the tile size based on resolution and grid size
# tile_width = res * grid_size[0]
# tile_height = res * grid_size[1]

# Initialize tile counters
chunk_counter = 0

# Iterate over the dataset row by row (top-left to bottom-right)
y_current = y_max  # Start at the top of the dataset
while y_current > y_min:
    x_current = x_min  # Start at the left edge for each row
    while x_current < x_max:
        # Define the bounding box for the current tile
        bbox_x_min = x_current
        bbox_x_max = x_current + tile_size
        bbox_y_min = y_current - tile_size
        bbox_y_max = y_current

        print(f"Processing Tile {chunk_counter}: X({bbox_x_min}, {bbox_x_max}), Y({bbox_y_min}, {bbox_y_max})")

        # Collect points within the bounding box
        points_x, points_y, points_z = [], [], []
        with laspy.open(las_file_path) as las:
            for points in las.chunk_iterator(subset_points):  # Process in manageable chunks
                mask = (
                    (points.x >= bbox_x_min) & (points.x < bbox_x_max) &
                    (points.y >= bbox_y_min) & (points.y < bbox_y_max)
                )
                points_x.append(points.x[mask])
                points_y.append(points.y[mask])
                points_z.append(points.z[mask])

        # Combine points from all chunks
        points_x = np.hstack(points_x)
        points_y = np.hstack(points_y)
        points_z = np.hstack(points_z)

        # Skip tiles with insufficient points
        if len(points_x) == 0:
            print(f"Tile {chunk_counter} skipped due to insufficient points.")
            x_current += (tile_size - overlap)
            continue

        # Create the grid for interpolation
        grid_x, grid_y = np.meshgrid(
            np.linspace(bbox_x_min, bbox_x_max, grid_size[0]),
            np.linspace(bbox_y_min, bbox_y_max, grid_size[1])
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
        dem_tif_path = f"{output_tif_dir}/dem_{chunk_counter}.tif"
        with rasterio.open(
            dem_tif_path, 'w',
            driver='GTiff',
            height=dem.shape[0],
            width=dem.shape[1],
            count=1,
            dtype='float32',
            crs=crs,
            transform=transform
        ) as out_image:
            out_image.write(dem, 1)

        print(f"DEM {chunk_counter} saved to {dem_tif_path}")

        # Visualize the DEM with Matplotlib
        dem_png_path = f"{output_png_dir}/dem_{chunk_counter}.png"
        plt.figure(figsize=(10, 10))
        plt.imshow(dem, cmap='gist_earth', origin='lower')
        plt.colorbar(label='Elevation (m)')
        plt.title(f'Digital Elevation Model {chunk_counter}', fontweight='bold')
        plt.xlabel("X coords")
        plt.ylabel("Y coords")
        plt.savefig(dem_png_path)
        plt.close()

        print(f"DEM visualization {chunk_counter} saved to {dem_png_path}")

        # Increment the chunk counter and move to the next tile
        chunk_counter += 1
        x_current += (tile_size - overlap)

    # Move to the next row
    y_current -= (tile_size - overlap)

print(f"Processed {chunk_counter} DEMs.")
