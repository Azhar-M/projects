import laspy
import sqlite3
from pyproj import Transformer

# File paths
las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"
reference_db_path = r'C:\Users\User\Documents\azhar_local_code\ikeja\projects\sqlite_bbox\reference_table\bbox_reference.db'

# Function to convert coordinates to Lon/Lat
def run(x, y, crs_from="EPSG:32735", crs_to="EPSG:4326"):
    transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lon, lat

# Step 1: Load the reference table
ref_con = sqlite3.connect(reference_db_path)
ref_cur = ref_con.cursor()

# Fetch all bbox metadata
cmd_ref_bbox = '''SELECT 
              bbox_id,
              min_x,
              max_x, min_y,
              max_y,
              f_path
              FROM reference_table
             '''

ref_cur.execute(cmd_ref_bbox)
bbox_data = ref_cur.fetchall()  # List of tuples: (bbox_id, min_x, max_x, min_y, max_y, f_path)
ref_con.close()


chunk_size = 10_000_000  # Number of points per chunk
with laspy.open(las_file_path) as las:
    for points in las.chunk_iterator(chunk_size):  # Process in chunks
        for i in range(len(points.x)):  # Iterate over points in the chunk
            x, y, z = points.x[i], points.y[i], points.z[i]

            # Step 3: Find which bbox contains this point
            for bbox_id, min_x, max_x, min_y, max_y, f_path in bbox_data:
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    # The point is inside this bounding box
                    lon, lat = run(x, y)  # Convert (x, y) to (lon, lat)

                    # Insert into the corresponding points table
                    bbox_con = sqlite3.connect(f_path)
                    bbox_cur = bbox_con.cursor()

                    bbox_cur.execute('''
                        INSERT INTO points (x_m, y_m, z_m, lon, lat)
                        VALUES (?, ?, ?, ?, ?);
                    ''', (x, y, z, lon, lat))

                    bbox_con.commit()
                    bbox_con.close()

                    print(f"Point ({x}, {y}, {z}) added to bbox {bbox_id}")
                    break  # Exit the loop after finding the matching bbox

print("All points processed and inserted.")
