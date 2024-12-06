import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np
import math

# Open the sample DEM TIFF file
dem_data = rasterio.open(r"C:\Users\User\Documents\azhar_local_code\ikeja\tiff\tmb1.tif")
dem_array = dem_data.read(1)
transform = dem_data.transform


bounds = dem_data.bounds
print(f"Bounds of the DEM: {bounds}")


shape = dem_array.shape
print(f"Shape of the DEM array: {shape}")


print(f"Transform of the DEM: {transform}")

# Choose transmitter coordinates near the center of the DEM's geographic extent
transmitter_x = (bounds.left + bounds.right) / 2
transmitter_y = (bounds.bottom + bounds.top) / 2

print(f"Transmitter coordinates (geographic): ({transmitter_x}, {transmitter_y})")

# Transforming geographic coordinates into grid coordinates
inv_transform = ~transform
transmitter_x, transmitter_y = [
    int(round(coord)) for coord in inv_transform * (transmitter_x, transmitter_y)]

# Check if the transformed coordinates are within bounds
if not (0 <= transmitter_x < shape[1] and 0 <= transmitter_y < shape[0]):
    raise ValueError(f"Transmitter coordinates ({transmitter_x}, {transmitter_y}) are out of bounds")

print(f"Transmitter coordinates in grid: ({transmitter_x}, {transmitter_y})")

# Define the integer to add to the current z value
z_increment = 30 

# Retrieve the current z value at the transmitter's location
current_z_value = dem_array[transmitter_y, transmitter_x]

# Calculate the new z value for the transmitter
transmitter_z = current_z_value + z_increment

# Assign the new z value to the transmitter's location in the DEM array
dem_array[transmitter_y, transmitter_x] = transmitter_z

def is_visible(dem_array, x1, y1, x2, y2):
    """Determine if the point (x2, y2) is visible from (x1, y1) in dem_array."""
    # If the start and end points are the same, return True
    if x1 == x2 and y1 == y2:
        return True

    # Calculate the number of steps for iteration based on the greater of dx or dy
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))

    # Handle the case when steps is zero
    if steps == 0:
        return False

    # Calculate the increments for x and y
    x_inc = dx / steps
    y_inc = dy / steps

    # Start from the source point
    x = x1
    y = y1

    # Height at the source point
    z = dem_array[int(y1), int(x1)] + 20

    # Iterate over the cells between source and target
    for i in range(1, int(steps)):
        x += x_inc
        y += y_inc

        # Calculate the elevation of the direct line at this point
        line_elevation = z + (dem_array[int(y2), int(x2)] - z) * (i / steps)

        # If the DEM elevation at this point is higher than the direct line, it's not visible
        if dem_array[int(y), int(x)] > line_elevation:
            return False

    return True

# Create an empty array for visibility
visibility_array = np.zeros_like(dem_array)

# Check visibility for each pixel
for x in range(dem_array.shape[1]):
    for y in range(dem_array.shape[0]):
        try:
            visibility_array[y, x] = is_visible(dem_array, transmitter_x, transmitter_y, x, y)
        except IndexError as e:
            print(f"IndexError at (x={x}, y={y}): {e}")
            visibility_array[y, x] = 0  # Mark as not visible if there's an error

# Write the visibility array to a new TIFF file
with rasterio.open(r"los.tif", 'w', **dem_data.meta) as dst:
    dst.write(visibility_array, 1)

# Plot the DEM data
plt.contour(dem_array, cmap='plasma')
plt.colorbar()
plt.title('Digital Elevation Model')
# 

# Plot the visibility analysis
plt.imshow(visibility_array, cmap='gray')
plt.colorbar()
plt.title('Line of Sight Analysis')

# Plot the transmitter location
plt.plot(transmitter_x, transmitter_y, 'ro')
# plt.show()

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

radius_meters = 600
radius_pixels = radius_meters / pixel_size_x_m

# Plot the 600m range circle
circle = plt.Circle((transmitter_x, transmitter_y), radius_pixels, color='blue', fill=False, linestyle='--')
plt.gca().add_patch(circle)

# Ensure the plot limits are set to show the entire map
plt.xlim(0, dem_array.shape[1])
plt.ylim(dem_array.shape[0], 0)  # Inverted y-axis for correct display
plt.show()