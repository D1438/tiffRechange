import numpy
from numpy.lib.npyio import save
import osgeo 
import numpy as np
from osgeo import osr, gdal
import sys
import os
from sys import argv
import glob, datetime
import time

start = time.time()

ds = [0] * (len(sys.argv) - 2)

for i in range(0, len(sys.argv) - 2):
    print('ds[', i, ']をオープン')
    ds[i] = gdal.Open(sys.argv[i + 1])

width = 1800
height = 1200

temperature_a = np.array([[[0.0 for i in range(1800)] for j in range(1200)] for k in range(len(ds))])

for i in range(0, len(ds)):
    temperature_pre = ds[i].GetRasterBand(1).ReadAsArray()
    print('temperature_pre[', i, ']の移し替え')
    for j in range(0, width):
        for k in range(0, height):
            if temperature_pre[k][j] >= -50.0:
                temperature_a[i][k][j] = temperature_pre[k][j]
            else:
                temperature_a[i][k][j] = 100.0

gt = ds[0].GetGeoTransform()

op_temperature = np.array([[100.0 for i in range(width)] for j in range(height)])
save_a = np.array([[0.0 for a in range(10)] for b in range(10)])
op_save_a = np.array([[100.0 for a in range(10)] for b in range(10)])

for i in range(0, len(ds)):
    print('temperature_a[', i, ']の加算中')
    for j in range(0, 120):
        for k in range(0, 180):
            
            for m in range(0, 10):
                for n in range(0, 10):
                    save_a[m][n] = temperature_a[i][j * 10 + m][k * 10 + n]
                    op_save_a[m][n] = op_temperature[j * 10 + m][k * 10 + n]
            
            unique, freq = np.unique(save_a, return_counts=True) #return_counts=Trueが肝
            min_num = unique[np.argmax(freq)] #freqの最も頻度が多い引数を取得して、uniqueから引っ張ってくる            
            
            op_unique, op_freq = np.unique(op_save_a, return_counts=True) #return_counts=Trueが肝
            op_mode = op_unique[np.argmax(op_freq)] #freqの最も頻度が多い引数を取得して、uniqueから引っ張ってくる
            
            if np.any(op_mode > min_num) == True:
                save_a.fill(min_num)
                
                for m in range(0, 10):
                    for n in range(0, 10):
                        op_temperature[j * 10 + m][k * 10 + n] = save_a[m][n]

for j in range(0, height):
    for k in range(0, width):
        if op_temperature[j][k] > 50.0:
            op_temperature[j][k] = -1000.0

print("書き込み中")
dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
band = 1 # バンド数
output = gdal.GetDriverByName('GTiff').Create(sys.argv[len(sys.argv) - 1], width, height, band, dtype) # 空の出力ファイル

output.SetGeoTransform((gt[0], 0.00833, 0, gt[3], 0, -0.00833)) # 座標系指定
srs = osr.SpatialReference() # 空間参照情報
srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

output.GetRasterBand(1).WriteArray(op_temperature)   # 赤バンド書き出し（b1はnumpy 2次元配列）
output.FlushCache()                     # ディスクに書き出し


elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
output = None