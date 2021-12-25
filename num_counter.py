import numpy
import osgeo 
import os
import numpy as np
from osgeo import osr, gdal
import sys
from sys import argv
import time


start = time.time()

op_array = [0.0 for m in range(130)]


a = [0 for n in range(len(sys.argv))]   #前

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

    max_temp = 0.0
    min_temp = 60.0
    
    """
    for j in range(0, height):
        for k in range(0, width):
            if temperature[j][k] > max_temp:
                max_temp = temperature[j][k]
            
            if temperature[j][k] < min_temp:
                min_temp = temperature[j][k]

    for j in range(0, height):
        for k in range(0, width):
            if temperature[j][k] != -1000:
                if temperature[j][k] > max_temp:
                    max_temp = temperature[j][k]
                
                if temperature[j][k] < min_temp:
                    min_temp = temperature[j][k]

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
    """
        
    for j in range(0, height):
        for k in range(0, width):
            if temperature[j][k] >= 0:
                l = int(temperature[j][k] / 0.2)
                op_array[i][int(l)] += 1
    
    

#print('最高潮目濃度 : ', max_temp)
#print('最低潮目濃度 : ', min_temp)

np.savetxt("/Users/ishizawadaisuke/Documents/graduate/temperture/csv/合成処理_0.2.csv", op_array, delimiter=",", fmt = '%f')

elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")