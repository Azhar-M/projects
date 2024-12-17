import matplotlib.pyplot as plt
import laspy
import sqlite3
from pyproj import Transformer  

import matplotlib.pyplot as plt
import laspy
import sqlite3
from pyproj import Transformer

# Function to convert coordinates to Lon/Lat
def run(left, bottom, right, top, crs_from="EPSG:32735", crs_to="EPSG:4326"):
    transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)
    top_left = transformer.transform(left, top)
    top_right = transformer.transform(right, top)
    bottom_right = transformer.transform(right, bottom)
    bottom_left = transformer.transform(left, bottom)
    return {
        "top_left": {"lng": top_left[0], "lat": top_left[1]},
        "top_right": {"lng": top_right[0], "lat": top_right[1]},
        "bottom_right": {"lng": bottom_right[0], "lat": bottom_right[1]},
        "bottom_left": {"lng": bottom_left[0], "lat": bottom_left[1]}
    }

# Initialize SQLite database connection
con = sqlite3.connect('bbox_grid.db')
cur = con.cursor()

# Path to your LAS file
las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"

# Tile parameters
tile_size = 500  # Size of each tile
overlap = 50     # Overlap size

# Extract bounding box coordinates
with laspy.open(las_file_path) as las:
    x_min, x_max = las.header.mins[0], las.header.maxs[0]
    y_min, y_max = las.header.mins[1], las.header.maxs[1]

print(f"x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")

# Initialize variables
bbox_id = 1
tiles = []

x_start = x_min
while x_start < x_max:
    y_start = y_max

    while y_start > y_min:
        x_end = x_start + tile_size
        y_end = y_start - tile_size

        # Convert the tile's coordinates to lon/lat
        tile_coords = run(x_start, y_end, x_end, y_start)

        tile = {
            "top_left": (x_start, y_start),
            "top_right": (x_end, y_start),
            "bottom_right": (x_end, y_end),
            "bottom_left": (x_start, y_end)
        }
        tiles.append(tile)


        # Create a table dynamically for each bbox_id
        table_name = f"bbox_{bbox_id}"
        cmd_create_table = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                top_left_x REAL, top_left_y REAL,
                top_right_x REAL, top_right_y REAL,
                bottom_right_x REAL, bottom_right_y REAL,
                bottom_left_x REAL, bottom_left_y REAL
            );
        '''
        cur.execute(cmd_create_table)

        # Insert the converted coordinates into the table
        cmd_insert = f'''
            INSERT or REPLACE INTO {table_name} (
                top_left_x, top_left_y,
                top_right_x, top_right_y,
                bottom_right_x, bottom_right_y,
                bottom_left_x, bottom_left_y
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        '''
        sql_params = (
            tile_coords["top_left"]["lng"], tile_coords["top_left"]["lat"],
            tile_coords["top_right"]["lng"], tile_coords["top_right"]["lat"],
            tile_coords["bottom_right"]["lng"], tile_coords["bottom_right"]["lat"],
            tile_coords["bottom_left"]["lng"], tile_coords["bottom_left"]["lat"]
        )
        cur.execute(cmd_insert, sql_params)
        con.commit()

        print(f"Inserted tile {bbox_id} into table {table_name}")

        bbox_id += 1
        y_start -= (tile_size - overlap)

    x_start += (tile_size - overlap)

# Close the database connection
con.close()
# Plot all the tiles

con = sqlite3.connect('bbox_grid.db')
cur = con.cursor()

plt.figure(figsize=(12, 12))

# Loop over all bbox tables and plot their coordinates
for bbox_id in range(1, bbox_id):  # Assuming bbox_id incremented till the last tile
    table_name = f"bbox_{bbox_id}"

    # Fetch the tile coordinates from the table
    cur.execute(f'''
        SELECT 
            top_left_x, top_left_y, 
            top_right_x, top_right_y, 
            bottom_right_x, bottom_right_y, 
            bottom_left_x, bottom_left_y 
        FROM {table_name};
    ''')
    row = cur.fetchone()

    if row:
        # Extract the coordinates
        top_left = (row[0], row[1])
        top_right = (row[2], row[3])
        bottom_right = (row[4], row[5])
        bottom_left = (row[6], row[7])

        # Define the X and Y coordinates for plotting
        x_coords = [top_left[0], top_right[0], bottom_right[0], bottom_left[0], top_left[0]]
        y_coords = [top_left[1], top_right[1], bottom_right[1], bottom_left[1], top_left[1]]

        # Plot the tile perimeter
        plt.plot(x_coords, y_coords, 'b-', alpha=0.6)

# Plot details
plt.title("Tiles in Longitude/Latitude (CRS Converted Grid)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.axis('equal')  # Ensure equal scaling for lon/lat
plt.show()

con.close()

# plt.figure(figsize=(12, 12))

# for tile in tiles:
#     # Extract tile corners
#     x_coords = [
#         tile["top_left"][0], tile["top_right"][0], 
#         tile["bottom_right"][0], tile["bottom_left"][0], 
#         tile["top_left"][0]  # Close the tile loop
#     ]
#     y_coords = [
#         tile["top_left"][1], tile["top_right"][1], 
#         tile["bottom_right"][1], tile["bottom_left"][1], 
#         tile["top_left"][1]  # Close the tile loop
#     ]
#     # Plot the tile perimeter
#     plt.plot(x_coords, y_coords, 'b-')
#     plt.axis('equal')

# # Add labels and grid
# plt.xlabel("X")
# plt.ylabel("Y")
# plt.title("Tiles with Overlap")
# plt.grid()
# plt.show()



# import laspy
# import numpy as np
# import rasterio
# from rasterio.transform import Affine
# from rasterio.crs import CRS
# from scipy.interpolate import griddata
# import matplotlib.pyplot as plt

# las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"

# top_left,top_right,bottom_left,bottom_right = [],[],[],[]

# with laspy.open(las_file_path) as las:
#     x_min, x_max = las.header.mins[0], las.header.maxs[0]
#     y_min, y_max = las.header.mins[1], las.header.maxs[1]

#     print(x_min, x_max, y_min, y_max)

#     for i in range(4):

#         tile_ix = x_min
#         tile_fx = x_min + 500

#         tile_iy = y_min
#         tile_fy = y_min - 500

#         top_left.append({tile_ix, tile_iy})
#         top_right.append({tile_fx, tile_iy})
#         bottom_left.append({tile_ix, tile_fy})
#         bottom_right.append({tile_fx, tile_fy})

#         print(tile_ix, tile_fx, tile_iy, tile_fy)

#         next_tile_ix = tile_fx
#         next_tile_fx = tile_fx + 500

#         next_tile_iy = tile_fy
#         next_tile_fy = tile_fy - 500


