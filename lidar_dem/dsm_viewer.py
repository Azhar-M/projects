import rasterio
import matplotlib.pyplot as plt

# File path to the DSM
dsm_tif_path = r"C:\Users\User\Downloads\TB-01-DSM(UTM35S)\TB-01-DSM(UTM35S).tif"

# Open the DSM using rasterio
with rasterio.open(dsm_tif_path) as src:
    dsm_data = src.read(1)  # Read the first band
    dsm_crs = src.crs       # Get CRS information
    dsm_bounds = src.bounds # Get bounds

# Visualize the DSM
plt.figure(figsize=(10, 10))
plt.imshow(dsm_data, cmap='gist_earth', origin='upper')
plt.colorbar(label='Elevation (m)')
plt.title('Digital Surface Model (DSM)', fontweight='bold')
plt.xlabel("X coords")
plt.ylabel("Y coords")
plt.savefig(r'C:\Users\User\Documents\azhar_local_code\ikeja\projects\png\dsm.png')
# plt.show()

print(f"DSM CRS: {dsm_crs}")
print(f"DSM Bounds: {dsm_bounds}")
