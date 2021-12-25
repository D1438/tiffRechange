import numpy
import osgeo 
import numpy as np
from osgeo import osr, gdal
import sys
from sys import argv
import time

start = time.time()

for i in range(1, len(sys.argv)):
    ds = gdal.Open(sys.argv[i])

    temperature = ds.GetRasterBand(1).ReadAsArray()

    width = 4993
    height = 2347

    width_ind = ds.RasterXSize
    height_ind = ds.RasterYSize

    gt = ds.GetGeoTransform()

    print('temperature_opを作成中')
    temperature_op = np.array([[-1000.0 for j in range(width)] for k in range(height)])

    minxnum = 104.11667
    minynum = 31.9

    minxnum_ind = gt[0]
    minynum_ind = gt[3]

    width_start = int((minxnum_ind - minxnum) / 0.00833)
    width_end = int(width_start + width_ind)
    height_start = int((minynum - minynum_ind) / 0.00833)
    height_end = int(height_start + height_ind)

    print('置き換え中')

    for j in range(width_start, width_end):
        for k in range(height_start, height_end):
            temperature_op[k][j] = temperature[k - height_start][j - width_start]

    print(sys.argv[i], ' を書き出し中')

    dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
    band = 1 # バンド数
    output = gdal.GetDriverByName('GTiff').Create(sys.argv[i], width, height, band, dtype) # 空の出力ファイル

    output.SetGeoTransform((minxnum, 0.00833, 0, minynum, 0, -0.00833)) # 座標系指定
    srs = osr.SpatialReference() # 空間参照情報
    srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
    output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

    output.GetRasterBand(1).WriteArray(temperature_op)   # 赤バンド書き出し（b1はnumpy 2次元配列）
    output.FlushCache()                     # ディスクに書き出し
    output = None



elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")