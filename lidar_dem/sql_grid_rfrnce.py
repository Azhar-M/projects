import matplotlib.pyplot as plt
import laspy
import sqlite3
from pyproj import Transformer  


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


ref_db_path = f'C:\\Users\\User\\Documents\\azhar_local_code\\ikeja\\projects\\sqlite_bbox\\reference_table\\bbox_reference.db'
ref_con = sqlite3.connect(ref_db_path)
ref_cur = ref_con.cursor()

cmd_rfrnce = '''
                CREATE TABLE IF NOT EXISTS reference_table (
                    min_x REAL,
                    max_x REAL,
                    min_y REAL,
                    max_y REAL,
                    f_path TEXT
                );
            '''
ref_cur.execute(cmd_rfrnce)
ref_con.commit()


las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"


# Tile parameters
tile_size = 500  # Size of each tile
overlap = 50     # Overlap size

# Extract bounding box coordinates
with laspy.open(las_file_path) as las:
    x_min, x_max = las.header.mins[0], las.header.maxs[0]
    y_min, y_max = las.header.mins[1], las.header.maxs[1]


x_start = x_min
while x_start < x_max:
    y_start = y_max

    while y_start > y_min:
        x_end = x_start + tile_size
        y_end = y_start - tile_size

        # Convert the tile's coordinates to lon/lat
        tile_coords = run(x_start, y_end, x_end, y_start)

        min_x = tile_coords['bottom_left']['lng']
        max_x = tile_coords['top_right']['lng']
        min_y = tile_coords['bottom_left']['lat']
        max_y = tile_coords['top_right']['lat']