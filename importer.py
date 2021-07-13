import osgeo
from osgeo import osr, gdal
import numpy as np

ds1 = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-01-02.tif', gdal.GA_ReadOnly)
ds2 = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-01-13.tif', gdal.GA_ReadOnly)
temperature1 = ds1.GetRasterBand(1)
temperature1_a = temperature1.ReadAsArray()
temperature2 = ds2.GetRasterBand(1)
temperature2_a = temperature2.ReadAsArray()

width1 = temperature1_a.shape[1]
height1 = temperature1_a.shape[0]
width2 = temperature2_a.shape[1]
height2 = temperature2_a.shape[0]

#print(ds1.GetGeoTransform())
#print(ds1.GetProjection())

gt = ds1.GetGeoTransform()
#print(gt)


output_a = [[]]

#for i in (0, width1-1): 
#    for j in (0, height1-1):
        
        

a = np.array([ds1.GetRasterBand(i + 1).ReadAsArray() for i in range(ds1.RasterCount)])

#print("tmp1_a")
#print(temperature1_a)
#print("tmp2_a")
#print(temperature2_a)

#print(a)
#print(a.shape)
#print(ds.RasterXSize, ds.RasterYSize)
#print(np.max(a), np.min(a))
#print(ds.GetGeoTransform())