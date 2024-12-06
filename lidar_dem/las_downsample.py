import laspy
import numpy as np

input_path = r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las"
output_path = r"C:\Users\User\Downloads\downsample.las"

# Open LAS file
with laspy.open(input_path) as las:
    header = las.header
    points = las.read_points(100000000)

# Downsample by taking every 10th point
downsampled_points = points[::18]

# Save downsampled LAS file
with laspy.create(output_path, header) as las_out:
    las_out.write_points(downsampled_points)

print(f"Downsampled LAS file saved to {output_path}")
