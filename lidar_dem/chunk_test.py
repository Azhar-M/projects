import laspy
import numpy as np
from pyproj import Transformer

# import rasterio
# from rasterio.transform import Affine
# from rasterio.crs import CRS
# from scipy.interpolate import griddata
# import matplotlib.pyplot as plt

# # File paths
# las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"
# output_tif_dir = r'C:\Users\User\Documents\azhar_local_code\ikeja\tiff\chunked'
# output_png_dir = r'C:\Users\User\Documents\azhar_local_code\ikeja\projects\png\chunked_png'

# # Fixed settings
# # subset_points = 1000  # Number of points to process per tile
# grid_size = (600, 400)  # Output DEM dimensions (width x height)
# res = 1  # 1-meter resolution
# total_points_limit = 100   # Total points to process
# chunk_size = 10            # Number of points to process at a time
# processed_points_count = 0 # Counter to track processed points

# # Load LAS file metadata
# with laspy.open(las_file_path) as las:
#     x_min, x_max = las.header.mins[0], las.header.maxs[0]
#     y_min, y_max = las.header.mins[1], las.header.maxs[1]

# # Calculate the tile size based on resolution and grid size
# tile_width = res * grid_size[0]
# tile_height = res * grid_size[1]

# # Initialize tile counters
# chunk_counter = 0

# # Iterate over the dataset row by row (top-left to bottom-right)
# y_current = y_max  # Start at the top of the dataset
# while y_current > y_min:
#     x_current = x_min  # Start at the left edge for each row
#     while x_current < x_max:
#         # Define the bounding box for the current tile
#         bbox_x_min = x_current
#         bbox_x_max = x_current + tile_width
#         bbox_y_min = y_current - tile_height
#         bbox_y_max = y_current

#         print(f"Processing Tile {chunk_counter}: X({bbox_x_min}, {bbox_x_max}), Y({bbox_y_min}, {bbox_y_max})")

#         # Collect points within the bounding box
#         points_x, points_y, points_z = [], [], []
#         with laspy.open(las_file_path) as las:
#             for points in las.chunk_iterator(chunk_size):  # Process in smaller chunks
#                 if processed_points_count >= total_points_limit:
#                     break  # Stop after processing 100 points

#                 # Filter points within the bounding box
#                 mask = (
#                     (points.x >= bbox_x_min) & (points.x < bbox_x_max) &
#                     (points.y >= bbox_y_min) & (points.y < bbox_y_max)
#                 )

#                 # Append filtered points
#                 filtered_x = points.x[mask]
#                 filtered_y = points.y[mask]
#                 filtered_z = points.z[mask]

#                 # Limit to remaining points needed
#                 remaining_points = total_points_limit - processed_points_count
#                 if len(filtered_x) > remaining_points:
#                     filtered_x = filtered_x[:remaining_points]
#                     filtered_y = filtered_y[:remaining_points]
#                     filtered_z = filtered_z[:remaining_points]

#                 # Append to the lists
#                 points_x.append(filtered_x)
#                 points_y.append(filtered_y)
#                 points_z.append(filtered_z)

#                 # Print points in this iteration
#                 print(f"Iteration {processed_points_count // chunk_size + 1}:")
#                 for i in range(len(filtered_x)):
#                     print(f"Point {processed_points_count + i + 1}: X={filtered_x[i]}, Y={filtered_y[i]}, Z={filtered_z[i]}")

#                 # Update the total processed points count
#                 processed_points_count += len(filtered_x)

#                 # Stop if the total limit is reached
#                 if processed_points_count >= total_points_limit:
#                     break

#         # Combine points from all chunks
#         points_x = np.hstack(points_x)
#         points_y = np.hstack(points_y)
#         points_z = np.hstack(points_z)

#         # Skip tiles with insufficient points
#         if len(points_x) == 0:
#             print(f"Tile {chunk_counter} skipped due to insufficient points.")
#             x_current += tile_width
#             continue

#         # Create the grid for interpolation
#         grid_x, grid_y = np.meshgrid(
#             np.linspace(bbox_x_min, bbox_x_max, grid_size[0]),
#             np.linspace(bbox_y_min, bbox_y_max, grid_size[1])
#         )

#         # Interpolate the elevation data
#         dem = griddata(
#             points=np.column_stack((points_x, points_y)),
#             values=points_z,
#             xi=(grid_x, grid_y),
#             method='linear'
#         )

#         # Fill NaN values with the minimum elevation or 0
#         dem = np.nan_to_num(dem, nan=np.nanmin(dem))

#         # Apply affine transformation for georeferencing
#         transform = Affine.translation(bbox_x_min - res / 2, bbox_y_min - res / 2) * Affine.scale(res, res)
#         crs = CRS.from_epsg(32735)

#         # Save the DEM as a GeoTIFF
#         dem_tif_path = f"{output_tif_dir}/dem_{chunk_counter}.tif"
#         with rasterio.open(
#             dem_tif_path, 'w',
#             driver='GTiff',
#             height=dem.shape[0],
#             width=dem.shape[1],
#             count=1,
#             dtype='float32',
#             crs=crs,
#             transform=transform
#         ) as out_image:
#             out_image.write(dem, 1)

#         print(f"DEM {chunk_counter} saved to {dem_tif_path}")

#         # Visualize the DEM with Matplotlib
#         dem_png_path = f"{output_png_dir}/dem_{chunk_counter}.png"
#         plt.figure(figsize=(10, 10))
#         plt.imshow(dem, cmap='gist_earth', origin='lower')
#         plt.colorbar(label='Elevation (m)')
#         plt.title(f'Digital Elevation Model {chunk_counter}', fontweight='bold')
#         plt.xlabel("X coords")
#         plt.ylabel("Y coords")
#         plt.savefig(dem_png_path)
#         plt.close()

#         print(f"DEM visualization {chunk_counter} saved to {dem_png_path}")

#         # Increment the chunk counter and move to the next tile
#         chunk_counter += 1
#         x_current += tile_width

#     # Move to the next row
#     y_current -= tile_height

# print(f"Processed {chunk_counter} DEMs.")


def run(lat,long):

    # Initialize a transformer from EPSG:4326 to EPSG:32735
    transformer = Transformer.from_crs("EPSG:32735","EPSG:4326",  always_xy=True)

    # Sample longitude and latitude from Mapbox click event
    # should take an input from mapbox click event
    # longitude, latitude = -26.024724834929252, 28.21292582324665  # Replace with actual click coordinates

    # Convert to EPSG:32735
    utm_x, utm_y = transformer.transform(long, lat)

    # print(f" X={utm_x}, Y={utm_y}")

    return utm_x, utm_y



# File paths
las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"

# Settings
total_points_limit = 100   # Total points to process
chunk_size = 10            # Number of points to process at a time
processed_points_count = 0 # Counter to track processed points

# Load LAS file metadata
with laspy.open(las_file_path) as las:

    # Iterate over chunks in the LAS file
    for points in las.chunk_iterator(chunk_size):
        # Get point coordinates
        points_x = points.x
        points_y = points.y
        points_z = points.z

        # Combine coordinates into readable tuples
        point_tuples = list(zip(points_x, points_y, points_z))

        # Print the current chunk of points
        print(f"Processed Chunk (up to {chunk_size} points):")
        for i, (x, y, z) in enumerate(point_tuples):
            print(f"Point {processed_points_count + i + 1}: X={x}, Y={y}, Z={z}")
            print( run(y,x))
        
        # Update the total count
        processed_points_count += len(point_tuples)

        # Stop after reaching the total limit
        if processed_points_count >= total_points_limit:
            print("\nReached the total points limit. Stopping iteration.")
            break

print(f"\nTotal processed points: {processed_points_count}")

