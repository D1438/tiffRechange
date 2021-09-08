from osgeo import osr, gdal
import math
import numpy as np
import time
import sys
from sys import argv


def width_height_inserter(ds_num, width_num, height_num, i): 
    width_num[i] = ds_num[i].RasterXSize
    height_num[i] = ds_num[i].RasterYSize


# tifファイルを開く
start = time.time()
ds = [0] * (len(sys.argv) - 2)
kernel = 2

for i in range(0, len(sys.argv) - 2):
    print('ds[', i, ']をオープン')
    ds[i] = gdal.Open(sys.argv[i + 1])

old_cs= osr.SpatialReference()
old_cs.ImportFromWkt(ds[0].GetProjectionRef())


# 世界測地系の設定
wgs84_wkt = """
GEOGCRS["WGS 84",
    DATUM["World Geodetic System 1984",
        ELLIPSOID["WGS 84",6378137,298.257223563,
            LENGTHUNIT["metre",1]]],
    PRIMEM["Greenwich",0,
        ANGLEUNIT["degree",0.0174532925199433]],
    CS[ellipsoidal,2],
        AXIS["geodetic latitude (Lat)",north,
            ORDER[1],
            ANGLEUNIT["degree",0.0174532925199433]],
        AXIS["geodetic longitude (Lon)",east,
            ORDER[2],
            ANGLEUNIT["degree",0.0174532925199433]],
    ID["EPSG",4326]]"""
new_cs = osr.SpatialReference()
new_cs .ImportFromWkt(wgs84_wkt)


# 座標変換のcreate a transform object to convert between coordinate systems
transform = osr.CoordinateTransformation(old_cs,new_cs)


#widthとheightの宣言、代入
width = [0] * len(ds)
height = [0] * len(ds)

for i in range(0, len(ds)): 
    width_height_inserter(ds, width, height, i)


prewitt_x = np.array([[0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 1, 0, -1],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0]])

prewitt_x = np.array([[0, 0, -1, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0]])

temperature_x = np.array([[[-60.0 for i in range(width[k])] for j in range(height[k])] for k in range(0, len(ds) - 1)])
temperature_y = np.array([[[-60.0 for i in range(width[k])] for j in range(height[k])] for k in range(0, len(ds) - 1)])

for j in range(kernel, height - kernel):
        for k in range(kernel, width - kernel):
            if temperature[j][k] != -60.0:

                save_a = np.array([a[k - kernel:k + kernel + 1] for a in temperature[j - kernel:j + kernel + 1]])
                save_a = np.where(save_a != -60.0, save_a, temperature[j][k])

                temperature_x[j][k] = np.sum(save_a * kernel_x)
                temperature_y[j][k] = np.sum(save_a * kernel_y)

                op_temperature[j][k] = np.sqrt(temperature_x[j][k] ** 2 + temperature_y[j][k] ** 2)
