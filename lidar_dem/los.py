import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np
import math

dem_data = rasterio.open(r"sample_dem.tif")
dem_array = dem_data.read(1)
transform = dem_data.transform
 
# Plot DEM data

 
 
def is_visible(dem_array, x1, y1, x2, y2):
    """Determine if the point (x2, y2) is visible from (x1, y1) in dem_array."""

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
 
 
# Define transmitter coordinates
transmitter_x, transmitter_y = 5,5 # Example coordinates
 
 
# Transforming lat long into grid coordinates
inv_transform = ~transform
transmitter_x, transmitter_y = [
    int(round(coord)) for coord in inv_transform * (transmitter_x, transmitter_y)]
 
# Create an empty array for visibility
visibility_array = np.zeros_like(dem_array)
 
# Check visibility for each pixel
for x in range(dem_array.shape[1]):
    for y in range(dem_array.shape[0]):
        visibility_array[y, x] = is_visible(
            dem_array, transmitter_x, transmitter_y, x, y)
 
 
with rasterio.open(r"los.tif", 'w', **dem_data.meta) as dst:
    dst.write(visibility_array, 1)



plt.contour(dem_array, cmap='YlGnBu')
plt.colorbar()
plt.title('Digital Elevation Model')
# plt.show()

 
plt.imshow(visibility_array, cmap='gray')
plt.colorbar()
plt.title('Line of Sight Analysis')

plt.plot(transmitter_x, transmitter_y, 'ro')
plt.grid()
plt.show()



# transmitter_x, transmitter_y = 76.601223, 31.511153