import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np
import math

# Open the sample DEM TIFF file
dem_data = rasterio.open(r"tmb1.tif")
dem_array = dem_data.read(1)
transform = dem_data.transform

bounds = dem_data.bounds
shape = dem_array.shape

# Choose transmitter coordinates near the center of the DEM's geographic extent
transmitter_x = (bounds.left + bounds.right) / 2
transmitter_y = (bounds.bottom + bounds.top) / 2

# Transforming geographic coordinates into grid coordinates
inv_transform = ~transform
transmitter_x, transmitter_y = [
    int(round(coord)) for coord in inv_transform * (transmitter_x, transmitter_y)]

# Check if the transformed coordinates are within bounds
if not (0 <= transmitter_x < shape[1] and 0 <= transmitter_y < shape[0]):
    raise ValueError(f"Transmitter coordinates ({transmitter_x}, {transmitter_y}) are out of bounds")

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
    if x1 == x2 and y1 == y2:
        return True

    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))

    if steps == 0:
        return False

    x_inc = dx / steps
    y_inc = dy / steps

    x = x1
    y = y1

    z = dem_array[int(y1), int(x1)] + 20

    for i in range(1, int(steps)):
        x += x_inc
        y += y_inc

        line_elevation = z + (dem_array[int(y2), int(x2)] - z) * (i / steps)

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

# Calculate the pixel size in meters
pixel_size_x_deg = transform[0]
pixel_size_y_deg = -transform[4]  # Negative because the y-coordinate decreases as you go down

# Assuming the DEM is centered around a specific latitude
center_lat = (bounds.top + bounds.bottom) / 2

# Convert pixel size from degrees to meters
meters_per_degree_lat = 111000  # Approximate value
meters_per_degree_lon = 111000 * math.cos(math.radians(center_lat))

pixel_size_x_m = pixel_size_x_deg * meters_per_degree_lon
pixel_size_y_m = pixel_size_y_deg * meters_per_degree_lat

# Calculate the radius in pixels
radius_meters = 600
radius_pixels = radius_meters / pixel_size_y_m
print(f"radius pixels {radius_pixels}")

# Create a mask for the circle
y_indices, x_indices = np.ogrid[:dem_array.shape[0], :dem_array.shape[1]]
distance_from_center = np.sqrt((x_indices - transmitter_x)**2 + (y_indices - transmitter_y)**2)
circle_mask = distance_from_center <= radius_pixels
print(circle_mask)

# Apply the mask to the visibility array
masked_visibility_array = np.where(circle_mask, visibility_array, 0)
print(masked_visibility_array)

num_visible_pixels = np.sum(masked_visibility_array == 1)
num_non_visible_pixels = np.sum(masked_visibility_array == 0)
total_pixels_inside_circle = np.sum(circle_mask)

print(f"Number of visible pixels (value = 1) inside the circle: {num_visible_pixels}")
print(f"Number of non-visible pixels (value = 0) inside the circle: {num_non_visible_pixels}")
print(f"Total number of pixels inside the circle: {total_pixels_inside_circle}")

pixel_area = pixel_size_x_m * pixel_size_y_m
total_area = total_pixels_inside_circle * pixel_area
visible_area = num_visible_pixels * pixel_area
visibility_percentage = (visible_area / total_area) * 100

print(f"Total area inside the circle: {total_area} square meters")
print(f"Visible area inside the circle: {visible_area} square meters")
print(f"Visibility percentage inside the circle: {visibility_percentage:.2f}%")

# Write the masked visibility array to a new TIFF file
with rasterio.open(r"masked_los.tif", 'w', **dem_data.meta) as dst:
    dst.write(masked_visibility_array, 1)

# Plot the DEM data
plt.figure(figsize=(10, 10))
plt.contour(dem_array, cmap='plasma')
plt.colorbar()
# plt.title('Digital Elevation Model')

# Plot the masked visibility analysis
plt.imshow(masked_visibility_array, cmap='gray', alpha=0.8)
plt.colorbar()
plt.title('Line of Sight Analysis (Masked)')

# Plot the transmitter location
plt.plot(transmitter_x, transmitter_y, 'ro')

# Plot the 600m range circle
circle = plt.Circle((transmitter_x, transmitter_y), radius_pixels, color='blue', fill=False, linestyle='--')
plt.gca().add_patch(circle)

# Ensure the plot limits are set to show the entire map
plt.xlim(0, dem_array.shape[1])
plt.ylim(dem_array.shape[0], 0)  # Inverted y-axis for correct display

# plt.imshow(visibility_array, cmap='gray')
# plt.contour(circle_mask, colors='red')
# plt.title('Visibility Array with Circle Mask')

plt.show()