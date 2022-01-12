import numpy
import osgeo 
import numpy as np
from osgeo import osr, gdal
import sys
from sys import argv
import time



print("gridの計算スタート")
start = time.time()

for i in range(1, len(sys.argv)):

    print(sys.argv[i], "を処理中")
    ds = gdal.Open(sys.argv[i])

    temperature = ds.GetRasterBand(1).ReadAsArray()

    width = ds.RasterXSize
    height = ds.RasterYSize

    gt = ds.GetGeoTransform()

    op_temperature = np.array([[0.0 for i in range(width)] for j in range(height)])

    for j in range(0, 120):
        for k in range(0, 180):
            save_a = np.array([a[k * 10:(k + 1) * 10] for a in temperature[j * 10:(j + 1) * 10]])

            if np.any(save_a < 0) == False:
                max_num = np.amax(save_a)
                min_num = 100.0
                
                # 最小値算出
                for m in range(0, 10):
                    for n in range(0, 10):
                        if save_a[m][n] < min_num:
                            min_num = save_a[m][n]
                
                #水温差の算出と代入
                save_a.fill(max_num - min_num)

                #opへの水温差の代入
                for m in range(0, 10):
                    for n in range(0, 10):
                        op_temperature[j * 10 + m][k * 10 + n] = save_a[m][n]
            else:
                #-1000があった時の処理
                for m in range(0, 10):
                    for n in range(0, 10):
                        op_temperature[j * 10 + m][k * 10 + n] = -1000.0


    dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
    band = 1 # バンド数
    output = gdal.GetDriverByName('GTiff').Create(sys.argv[i], width, height, band, dtype) # 空の出力ファイル

    output.SetGeoTransform((gt[0], 0.00833, 0, gt[3], 0, -0.00833)) # 座標系指定
    srs = osr.SpatialReference() # 空間参照情報
    srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
    output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

    output.GetRasterBand(1).WriteArray(op_temperature)   # 赤バンド書き出し（b1はnumpy 2次元配列）
    output.FlushCache()                     # ディスクに書き出し
    output = None
elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
