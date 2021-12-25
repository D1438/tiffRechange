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
    
    tem = np.array([[0 for l in range(90)] for n in range(60)])

    for j in range(0, 60):
        for k in range(0, 90):
            save_a = np.array([a[k * 20:(k + 1) * 20] for a in temperature[j * 20:(j + 1) * 20]])

            if np.any(save_a < -10) == False:
                max_num = np.amax(save_a)
                min_num = 100.0
                
                for m in range(0, 20):
                    for n in range(0, 20):
                        if save_a[m][n] < min_num:
                            min_num = save_a[m][n]
                
                save_a.fill(max_num - min_num)

                for m in range(0, 20):
                    for n in range(0, 20):
                        op_temperature[j * 20 + m][k * 20 + n] = save_a[m][n]
            else:
                for m in range(0, 20):
                    for n in range(0, 20):
                        op_temperature[j * 20 + m][k * 20 + n] = -1000.0


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


"""

            tem[j][k] = int(two_num / 80)
    
    np.set_printoptions(threshold=5400)
    print(tem)

"""