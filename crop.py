import osgeo
from osgeo import osr, gdal
import numpy as np
import sys
from sys import argv



ds = [0] * (len(sys.argv) - 1)

for i in range(1, len(ds) + 1):
    print('[', i, ']をオープン')
    ds = gdal.Open(sys.argv[i])

    temperature = ds.GetRasterBand(1).ReadAsArray()

    width = ds.RasterXSize
    height = ds.RasterYSize

    #print(width, height)
    gt = ds.GetGeoTransform()
    minx = round(gt[0], 5)
    maxy = round(gt[3], 5)
    #print(minx, maxy)
    
# 120.00198~134.99598 20.00033~29.99633
    op_minx = 120.00198
    #op_miny = 20.00033
    op_maxy = 29.99633
    op_width = 1800
    op_height = 1200
    op_temperature = np.array([[0.0 for i in range(op_width)] for j in range(op_height)])

    diff_width = round((op_minx - minx) / 0.00833)
    diff_height = round((maxy - op_maxy) / 0.00833)


    print('[', i, ']をクロッピング中')

    for j in range(0, op_height): 
        for k in range(0, op_width):
            op_temperature[j][k] = temperature[diff_height+j][diff_width+k]
    
    
    dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
    band = 1 # バンド数
    output = gdal.GetDriverByName('GTiff').Create(sys.argv[i], op_width, op_height, band, dtype) # 空の出力ファイル

    output.SetGeoTransform((op_minx, 0.00833, 0, op_maxy, 0, -0.00833)) # 座標系指定
    srs = osr.SpatialReference() # 空間参照情報
    srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
    output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

    output.GetRasterBand(1).WriteArray(op_temperature)   # 赤バンド書き出し（b1はnumpy 2次元配列）
    output.FlushCache()                     # ディスクに書き出し
    output = None
