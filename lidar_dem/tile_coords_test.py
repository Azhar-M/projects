import sqlite3
import matplotlib

import matplotlib.pyplot as plt

# Reopen database to fetch data for plotting
con = sqlite3.connect('bbox_grid.db')
cur = con.cursor()

plt.figure(figsize=(12, 12))
bbox_id = 1
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
        bbox_id += 1

# Plot details
plt.title("Tiles in Longitude/Latitude (CRS Converted Grid)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.axis('equal')  # Ensure equal scaling for lon/lat
plt.show()

con.close()
