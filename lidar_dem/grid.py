

import rasterio
import math

# Open the DEM file
dem_data = rasterio.open(r"tmb1.tif")

# Get the transform attribute which contains the pixel size
transform = dem_data.transform

# Pixel size in degrees
pixel_size_x_deg = transform[0]
pixel_size_y_deg = -transform[4]  # Negative because the y-coordinate decreases as you go down

# Assuming the DEM is centered around a specific latitude
# You can use the center latitude of the DEM for this calculation
bounds = dem_data.bounds
center_lat = (bounds.top + bounds.bottom) / 2

# Convert pixel size from degrees to meters
meters_per_degree_lat = 111000  # Approximate value
meters_per_degree_lon = 111000 * math.cos(math.radians(center_lat))

pixel_size_x_m = pixel_size_x_deg * meters_per_degree_lon
pixel_size_y_m = pixel_size_y_deg * meters_per_degree_lat

print(f"Pixel size: {pixel_size_x_m} meters by {pixel_size_y_m} meters")