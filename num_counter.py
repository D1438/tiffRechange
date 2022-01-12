import numpy
import osgeo 
import os
import math
import numpy as np
from osgeo import osr, gdal
import sys
from sys import argv
import time


start = time.time()

op_array = np.array([0 for m in range(30)])
#op_array = np.array([[0 for m in range(30)] for n in range(130)])

a = [0 for n in range(len(sys.argv))]   #前
max_temp = 0.0
min_temp = 60.0


for i in range(1, len(sys.argv)):
    count = 0
#   画像を読み込み
    print(sys.argv[i] + 'をオープン')
    #op_array[i - 1][0] = sys.argv[i]

    ds = gdal.Open(sys.argv[i])
    file_path = sys.argv[i]

    temperature = ds.GetRasterBand(1).ReadAsArray()

    width = ds.RasterXSize
    height = ds.RasterYSize

    #all_num = width * height * 1.0
    #minus_num = width * height * 1.0

    gt = ds.GetGeoTransform()
    
    for j in range(0, height):
        for k in range(0, width):
            if temperature[j][k] != -1000:
                if temperature[j][k] > max_temp:
                    max_temp = temperature[j][k]
                
                if temperature[j][k] < min_temp:
                    min_temp = temperature[j][k]
    """
    for j in range(0, height):
        for k in range(0, width):
            if temperature[j][k] == -1000.0:
                a[i - 1] += 1
    
    print(a[i - 1])
    
    for j in range(0, height):
        for k in range(0, width):

            if temperature[j][k] == -1000.0:
                minus_num -= 1.0

    op_array[i - 1] = (minus_num / all_num) * 100.0
    
    for j in range(0, height):
        for k in range(0, width):
            
            #if temperature[j][k] >= 0:
            #    l: int = int(temperature[j][k])
            #    op_array[l] += 1
            
            #temperature[j][k] = int(temperature[j][k])
            
            if temperature[j][k] > 40.0:
                temperature[j][k] = -1000.0
    
            if temperature[j][k] < -100.0:
                temperature[j][k] = -1000.0
    
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
    """



print('最高水温差 : ', max_temp)
print('最低水温差 : ', min_temp)

#np.savetxt("/Users/ishizawadaisuke/Documents/graduate/temperture/csv/合成処理_4月30日.csv", op_array, delimiter=",", fmt = '%d')

elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
