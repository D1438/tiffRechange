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

date = 4

for y in range(4, 31):
    n = datetime.datetime(2021, 4, date - 3)
    l = []

    for z in range(0, 7):
        pattern = n.strftime('%m-%d*')
        l += glob.glob(pattern)
        n += datetime.timedelta(days=1)

    ds = [0] * len(l)

    for i in range(0, len(l)):
        print(os.path.basename(l[i]) + "の編集")
        ds[i] = gdal.Open(l[i])

    width = 1800
    height = 1200

    temperature_a = np.array([[[0.0 for i in range(1800)] for j in range(1200)] for k in range(len(l))])

    for i in range(0, len(ds)):
        temperature_pre = ds[i].GetRasterBand(1).ReadAsArray()
        print('temperature_pre[', i, ']の移し替え')
        for j in range(0, width):
            for k in range(0, height):
                temperature_a[i][k][j] = temperature_pre[k][j]

    gt = ds[0].GetGeoTransform()

    op_temperature = np.array([[0.0 for i in range(width)] for j in range(height)])
    save_a = np.array([[0.0 for a in range(10)] for b in range(10)])


    for i in range(0, len(ds)):
        print('temperature_a[', i, ']の加算中')
        for j in range(0, 120):
            for k in range(0, 180):
                
                if np.any(save_a < 0.0) == False:
                    for m in range(0, 10):
                        for n in range(0, 10):
                            save_a[m][n] = temperature_a[i][j * 10 + m][k * 10 + n]
                    
                    if np.any(np.array([a[k * 10:(k + 1) * 10] for a in op_temperature[j * 10:(j + 1) * 10]]) > np.max(save_a)) == True:
                        save_a.fill(np.max(save_a))
                        
                        for m in range(0, 10):
                            for n in range(0, 10):
                                op_temperature[j * 10 + m][k * 10 + n] = save_a[m][n]

    for j in range(0, height):
        for k in range(0, width):
            if op_temperature[j][k] == 0.0:
                op_temperature[j][k] = -1000.0
    
    
    print("書き込み中")
    n = datetime.datetime(2021, 4, date)
    op_str = "/Users/ishizawadaisuke/Documents/graduate/temperture/処理合成/各日の水温差の合成_MAX値/" + n.strftime('%m-%d.tif')

    print("書き込み中")
    dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
    band = 1 # バンド数
    output = gdal.GetDriverByName('GTiff').Create(str(op_str), width, height, band, dtype) # 空の出力ファイル

    output.SetGeoTransform((gt[0], 0.00833, 0, gt[3], 0, -0.00833)) # 座標系指定
    srs = osr.SpatialReference() # 空間参照情報
    srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
    output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

    output.GetRasterBand(1).WriteArray(op_temperature)   # 赤バンド書き出し（b1はnumpy 2次元配列）
    output.FlushCache()                     # ディスクに書き出し
    
    date += 1

elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
output = None