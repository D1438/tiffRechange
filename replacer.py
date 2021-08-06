import numpy
import osgeo 
import numpy as np
from osgeo import osr, gdal
import sys
from sys import argv


for i in range(1, len(sys.argv)):
    print('[', i, ']をオープン')
    ds = gdal.Open(sys.argv[i])

    temperature = ds.GetRasterBand(1).ReadAsArray()

    width = ds.RasterXSize
    height = ds.RasterYSize

    gt = ds.GetGeoTransform()

    for j in range(0, height):
        for k in range(0, width):
            if temperature[j][k] == 0.0:
                temperature[j][k] = -60.0


    dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
    band = 1 # バンド数
    output = gdal.GetDriverByName('GTiff').Create(sys.argv[i], width, height, band, dtype) # 空の出力ファイル

    output.SetGeoTransform((gt[0], 0.00833, 0, gt[3], 0, -0.00833)) # 座標系指定
    srs = osr.SpatialReference() # 空間参照情報
    srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
    output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

    output.GetRasterBand(1).WriteArray(temperature)   # 赤バンド書き出し（b1はnumpy 2次元配列）
    output.FlushCache()                     # ディスクに書き出し
    output = None