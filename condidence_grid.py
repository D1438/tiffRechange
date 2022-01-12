from osgeo import osr, gdal
import os
import numpy as np
import time
import sys
from sys import argv


start = time.time()

for i in range(1, len(sys.argv)):
    print(os.path.basename(sys.argv[i]) + "の編集")
    
    ds = gdal.Open(sys.argv[i])
    gt = ds.GetGeoTransform()
    
    grid = ds.GetRasterBand(1).ReadAsArray()

    width = ds.RasterXSize
    height = ds.RasterYSize
    
    print("母平均の算出")
    #average算出の過程
    sum = 0     #average算出のためのsum
    count_except = 0      #-1000を除いたカウント
    
    for j in range(0, 120):
        for k in range(0, 180):
            save_a = np.array([a[k * 10:(k + 1) * 10] for a in grid[j * 10:(j + 1) * 10]])
            
            unique, freq = np.unique(save_a, return_counts=True) #return_counts=Trueが肝
            mode = unique[np.argmax(freq)] #freqの最も頻度が多い引数を取得して、uniqueから引っ張ってくる
            
            if mode != -1000:
                sum += mode
                count_except += 1
    
    average = sum / count_except      #全体の平均値

    #不偏分散算出の過程
    print("不偏分散の算出")
    UV_sum = 0

    for j in range(0, 120):
        for k in range(0, 180):
            save_b = np.array([a[k * 10:(k + 1) * 10] for a in grid[j * 10:(j + 1) * 10]])

            unique, freq = np.unique(save_b, return_counts=True) #return_counts=Trueが肝
            mode = unique[np.argmax(freq)] #freqの最も頻度が多い引数を取得して、uniqueから引っ張ってくる

            if mode != -1000:
                UV_sum += (mode - average) ** 2
    
    unbiased_variance = UV_sum / (count_except - 1)     #不偏分散

    confidence_interval = 2.576 * np.sqrt(unbiased_variance)       #信頼区間の+値

    print("grid作成")
    #信頼区間以下のgridの作成
    op_grid = np.array([[-1000.0 for i in range(width)] for j in range(height)])
    count = 0

    for j in range(0, 120):
        for k in range(0, 180):
            save_c = np.array([a[k * 10:(k + 1) * 10] for a in grid[j * 10:(j + 1) * 10]])

            unique, freq = np.unique(save_c, return_counts=True) #return_counts=Trueが肝
            mode = unique[np.argmax(freq)] #freqの最も頻度が多い引数を取得して、uniqueから引っ張ってくる

            if mode <= average + confidence_interval:
                for m in range(0, 10):
                    for n in range(0, 10):
                        op_grid[j * 10 + m][k * 10 + n] = mode
            else:
                count+= 1
    
    print(count)
    
    dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
    band = 1 # バンド数
    output = gdal.GetDriverByName('GTiff').Create(sys.argv[i], width, height, band, dtype) # 空の出力ファイル

    output.SetGeoTransform((gt[0], 0.00833, 0, gt[3], 0, -0.00833)) # 座標系指定
    srs = osr.SpatialReference() # 空間参照情報
    srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
    output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

    output.GetRasterBand(1).WriteArray(op_grid)   # 赤バンド書き出し（b1はnumpy 2次元配列）
    output.FlushCache()                     # ディスクに書き出し
    output = None

elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
output = None  