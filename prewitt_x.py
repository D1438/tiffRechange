import numpy
import osgeo 
import numpy as np
from osgeo import osr, gdal
import sys
from sys import argv
import time



start = time.time()
kernel = 1
#int(sys.argv[len(sys.argv) - 1])
count = kernel * 2 + 1

def prewitt_kernel_x_maker(kernel_num):
    array = np.array([[0.0 for a in range(count)] for b in range(count)])
    
    for i in range(count):
        array[i][0] = -1
        array[i][count - 1] = 1

    return array

def prewitt_kernel_y_maker(kernel_num):
    array = np.array([[0.0 for a in range(count)] for b in range(count)])
    
    for i in range(count):
        array[0][i] = -1
        array[count - 1][i] = 1

    return array


print('カーネル', kernel, 'の計算中')

kernel_x = np.array([[0, 0, 0],
                    [-1, 0, 1],
                    [0, 0, 0]])

kernel_y = np.array([[0, -1, 0],
                    [0, 0, 0],
                    [0, 1, 0]])

for i in range(1, len(sys.argv) - 1):
#   画像を読み込み
    print('[', i, ']をオープン')
    ds = gdal.Open(sys.argv[i])

    temperature = ds.GetRasterBand(1).ReadAsArray()

    width = ds.RasterXSize
    height = ds.RasterYSize

    temperature_x = np.array([[-60.0 for i in range(width)] for j in range(height)])
    #temperature_y = np.array([[-60.0 for i in range(width)] for j in range(height)])
    #op_temperature = np.array([[-60.0 for i in range(width)] for j in range(height)])

    gt = ds.GetGeoTransform()

    for j in range(kernel, height - kernel):
        for k in range(kernel, width - kernel):
            if temperature[j][k] != -60.0:

                save_a = np.array([a[k - kernel:k + kernel + 1] for a in temperature[j - kernel:j + kernel + 1]])
                save_a = np.where(save_a != -60.0, save_a, temperature[j][k])

                if np.sum(save_a * kernel_x) >= float(sys.argv[len(sys.argv) - 1]):
                    temperature_x[j][k] = 2
                else:
                    temperature_x[j][k] = 0


    dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
    band = 1 # バンド数
    output = gdal.GetDriverByName('GTiff').Create(sys.argv[i], width, height, band, dtype) # 空の出力ファイル

    output.SetGeoTransform((gt[0], 0.00833, 0, gt[3], 0, -0.00833)) # 座標系指定
    srs = osr.SpatialReference() # 空間参照情報
    srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
    output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

    output.GetRasterBand(1).WriteArray(temperature_x)   # 赤バンド書き出し（b1はnumpy 2次元配列）
    output.FlushCache()                     # ディスクに書き出し
    output = None
elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")

