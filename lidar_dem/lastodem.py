import pylas
import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS
# import earthpy.spatial as es
from scipy.interpolate import griddata 
# import matplotlib.pyplot as plt
# from matplotlib.cbook import get_sample_data
# from matplotlib.colors import LightSource

#Reading in the las file
las = pylas.read(r"C:\Users\User\Downloads\TB-01-Pointcloud(UTM35S-thinned)\TB-01-Pointcloud(UTM35S-thinned).las")


#Extracting the x,y coordinates as a list of tuples
points = np.column_stack((las.x, las.y))
elevation = las.z

# print(points)

# 10m resolution
res = 1

#Creating a grid
x_range = np.arange(las.x.min(),las.x.max() + res, res)
y_range = np.arange(las.y.min(),las.y.max() + res, res)

#Interpolating the elevation data
grid_x, grid_y = np.meshgrid(x_range,y_range)
dem = griddata(points,elevation,(grid_x,grid_y), method = 'linear')

#flips dem to preserve original orientation
# dem = np.flipud(dem)

# print(dem.shape)

# fig = plt.figure(figsize= [10,10])

# plt.imshow(dem,cmap = 'gist_earth', origin = 'lower')
# plt.colorbar(label = 'Elevation (m)')
# plt.title('Digital Elevation Model',fontweight = 'bold')
# plt.xlabel("X coords")
# plt.ylabel("Y coords")  
# plt.savefig(r'C:\Users\User\Documents\azhar_local_code\ikeja\projects\png\big_dem.png')
# plt.show()

las_vlr = las.vlrs
print(las_vlr)

crs = CRS.from_epsg(32735)
# print(crs.data)

# Affine transformation
transform = Affine.translation(grid_x[0][0]-res/2, grid_y[0][0] -res/2)*Affine.scale(res,res)

tif_path = r'C:\Users\User\Documents\azhar_local_code\ikeja\tiff\dem_big.tif'

#tif file creation
out_image = rasterio.open(tif_path,'w',
                          driver = 'GTiff',
                          height = dem.shape[0],
                          width = dem.shape[1],
                          count = 1,
                          dtype = dem.dtype,
                          crs = crs,
                          transform = transform)
out_image.write(dem,1)
out_image.close()
