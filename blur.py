import numpy
import osgeo 
import numpy as np
from osgeo import osr, gdal
import sys
from sys import argv
import time

start = time.time()
kernel = int(sys.argv[len(sys.argv) - 1])
count = (kernel * 2 + 1) * (kernel * 2 + 1)

print('カーネル', kernel, 'の計算中')

for i in range(1, len(sys.argv) - 1):
#   画像を読み込み
    print('[', i, ']をオープン')
    ds = gdal.Open(sys.argv[i])

    temperature = ds.GetRasterBand(1).ReadAsArray()



    width = ds.RasterXSize
    height = ds.RasterYSize

    op_temperature = np.array([[-60.0 for i in range(width)] for j in range(height)])

    gt = ds.GetGeoTransform()

    for j in range(kernel - 1, height - kernel):
        for k in range(kernel - 1, width - kernel):
            if temperature[j][k] != -60.0:
                ans = 0

                for m in range(-1 * kernel, kernel + 1):
                    for n in range(-1 * kernel, kernel + 1):
                        if temperature[j - m][k - n] != -60.0:
                            ans = ans + temperature[j - m][k - n]
                        else:
                            ans = ans + temperature[j][k]

                op_temperature[j][k] = ans/count


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



