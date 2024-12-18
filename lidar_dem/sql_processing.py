import laspy
import numpy as np
import rasterio
import sqlite3
import json
import time
from rasterio.transform import Affine
from rasterio.crs import CRS
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from pyproj import Transformer


logging_json = r'C:\Users\User\Documents\azhar_local_code\ikeja\projects\un_processed\failure_log.json'

last_processed_chunk = 0
unprocessed_points = []

if logging_json:
    try:
        with open(logging_json, 'r') as f:
            log_data = json.load(f)
            last_processed_chunk = log_data.get("last_processed_chunk", 0)
            unprocessed_points = log_data.get("unprocessed_points", [])
        print(f"Resuming from chunk {last_processed_chunk}")
    except FileNotFoundError:
        print("No previous failure log found. Starting from the beginning.")



timing = {
    "total": 0,
    "setup": 0,
    "chunk_processing": 0,
    "bbox_matching": 0,
    "db_insertion": 0,
    "crs_conversion": 0,
    "logging": 0
}

start_total = time.perf_counter()
start_setup = time.perf_counter()

def coords_convert(x, y, crs_from="EPSG:32735", crs_to="EPSG:4326"):
    transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lon, lat

las_file_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"

subset_points = 10_000_000 

ref_db_path = f'C:\\Users\\User\\Documents\\azhar_local_code\\ikeja\\projects\\sqlite_bbox\\reference_table\\bbox_reference.db'
ref_con = sqlite3.connect(ref_db_path)
ref_cur = ref_con.cursor()

bbox_db_path = f'C:\\Users\\User\\Documents\\azhar_local_code\\ikeja\\projects\\sqlite_bbox'

timing["setup"] = time.perf_counter() - start_setup

n = 0

with laspy.open(las_file_path) as las:
    N = las.header.point_records_count  #get total points of the las file

    for chunk_idx, point in enumerate(las.chunk_iterator(subset_points)):
        if chunk_idx < last_processed_chunk:
            continue  # Skip already processed chunks

        print(f"Processing chunk {chunk_idx}...")

        start_chunk = time.perf_counter()

        start_conversion = time.perf_counter()
        lon_list,lat_list = coords_convert(point.x,point.y) 
        timing["crs_conversion"] += time.perf_counter() - start_conversion

        for idx in range(len(lon_list)):
            n += 1

            lat = lat_list[idx]
            lon = lon_list[idx]
            x_m = point.x[idx]  
            y_m = point.y[idx]
            z_m = point.z[idx]

            # print(lat, lon)
   
            # bbox_con = sqlite3.connect(f_path)
            # bbox_cur = bbox_con.cursor()
            start_bbox_match = time.perf_counter()
            cmd_path = '''
                        SELECT f_path 
                        FROM reference_table 
                        WHERE min_x <= ? AND max_x >= ? AND min_y <= ? AND max_y >= ?;
                        '''
            ref_cur.execute(cmd_path, (lon, lon, lat, lat))
            res = ref_cur.fetchone()
            timing["bbox_matching"] += time.perf_counter() - start_bbox_match

            if res is None:
                # Log missing point
                unprocessed_points.append({
                    "lon": lon,
                    "lat": lat,
                    "x_m": x_m,
                    "y_m": y_m,
                    "z_m": z_m,
                    "chunk": idx,
                    "origin_file": las_file_path,
                    "reason": "No matching bbox"
                })
                continue  
            
            start_db_insert = time.perf_counter()
            f_path = res[0]

            try:
                bbox_con = sqlite3.connect(f_path)
                bbox_cur = bbox_con.cursor()

                cmd_bbox_insert = '''
                                    INSERT INTO points 
                                    (x_m, y_m, z_m, lon, lat)
                                    VALUES (?, ?, ?, ?, ?);
                                    '''
                sql_bbox_params = (x_m, y_m, z_m, lon, lat)

                bbox_cur.execute(cmd_bbox_insert, sql_bbox_params)
                bbox_con.commit()
                bbox_con.close()

                processed_bbox_files.add(f_path)

            # break  
            except Exception as e:
                # Log failed insert
                unprocessed_points.append({
                    "lon": lon,
                    "lat": lat,
                    "x_m": x_m,
                    "y_m": y_m,
                    "z_m": z_m,
                    "chunk": chunk_idx,
                    "origin_file": las_file_path,
                    "reason": f"Database error: {str(e)}"
                })
            timing["db_insertion"] += time.perf_counter() - start_db_insert


            if n % 10_000 == 0:
                print(f"Processed {n} of {N} points.")
                print(f"Point ({x_m}, {y_m}, {z_m}) added to bbox {f_path}")
            

        timing["chunk_processing"] += time.perf_counter() - start_chunk

        with open(logging_json, 'w') as f:
            json.dump({
                "last_processed_chunk": chunk_idx,
                "unprocessed_points": unprocessed_points
            }, f, indent=4)

        print(f"Chunk {chunk_idx} processed in {timing['chunk_processing']:.2f} seconds")


start_logging = time.perf_counter()


timing["logging"] = time.perf_counter() - start_logging

# Record total runtime
timing["total"] = time.perf_counter() - start_total









        
