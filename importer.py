import osgeo
from osgeo import gdal
import numpy as np

ds = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD2021070421170/GC1SG1_202104011308T29902_L2SG_SSTNK_2000_0000000000357129_SST.tif', gdal.GA_ReadOnly)
a = np.array([ds.GetRasterBand(i + 1).ReadAsArray() for i in range(ds.RasterCount)])
print(a)
print(a.shape)
print(ds.RasterXSize, ds.RasterYSize)
print(np.max(a), np.min(a))