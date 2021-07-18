from osgeo import osr, gdal
import math
import numpy as np
import time
import sys
from sys import argv


# 座標を各解像度の値に一番近い値に変換する
def normalize(resolution, parameter): # resolutionは解像度、parameterは各tifファイルの座標の最小最大値
    i = 0
    minimum = parameter

    while i < 180:
        now = abs(parameter - i)

        if now < minimum:
            minimum = now
            answer = i
        i = i + abs(resolution)

    return answer


def minimum_caluculation(min) -> float: #現状ね、
    a = min[0]
    for i in range(0, 2): 
        if a > min[i]: 
            a = min[i]
    
    return a

def maximum_caluculation(max) -> float: #現状ね、
    a = max[0]
    for i in range(0, 2): 
        if a < max[i]:
            a = max[i]
    
    return a

def float_to_int(num) -> int:
    if (num - int(num)) > 0.5: 
        num = math.ceil(num)
    elif (num - int(num)) < 0.5: 
        num = math.floor(num)
    
    return num


def min_max_caluculater(gt_num, width_num, height_num, i):
    miny[i] = normalize(gt_num[i][5], gt_num[i][3] + width_num[i]*gt_num[i][4] + height_num[i]*gt_num[i][5])
    minx[i] = normalize(gt_num[i][1], gt_num[i][0])
    maxx[i] = normalize(gt_num[i][1], gt_num[i][0] + width_num[i]*gt_num[i][1] + height_num[i]*gt_num[i][2])
    maxy[i] = normalize(gt_num[i][5], gt_num[i][3]) 



# tifファイルを開く
start = time.time()
ds = [0] * (len(sys.argv) - 1)


ds[0] = gdal.Open(sys.argv[1])
ds[1] = gdal.Open(sys.argv[2])
old_cs= osr.SpatialReference()
old_cs.ImportFromWkt(ds[0].GetProjectionRef())
old_cs.ImportFromWkt(ds[1].GetProjectionRef())

temperature1_a = ds[0].GetRasterBand(1).ReadAsArray()
temperature2_a = ds[1].GetRasterBand(1).ReadAsArray()


# 世界測地系の設定
wgs84_wkt = """
GEOGCRS["WGS 84",
    DATUM["World Geodetic System 1984",
        ELLIPSOID["WGS 84",6378137,298.257223563,
            LENGTHUNIT["metre",1]]],
    PRIMEM["Greenwich",0,
        ANGLEUNIT["degree",0.0174532925199433]],
    CS[ellipsoidal,2],
        AXIS["geodetic latitude (Lat)",north,
            ORDER[1],
            ANGLEUNIT["degree",0.0174532925199433]],
        AXIS["geodetic longitude (Lon)",east,
            ORDER[2],
            ANGLEUNIT["degree",0.0174532925199433]],
    ID["EPSG",4326]]"""
new_cs = osr.SpatialReference()
new_cs .ImportFromWkt(wgs84_wkt)


# 座標変換のcreate a transform object to convert between coordinate systems
transform = osr.CoordinateTransformation(old_cs,new_cs) 

#get the point to transform, pixel (0,0) in this case
width = [0] * 2
height = [0] * 2

width[0] = ds[0].RasterXSize
height[0] = ds[0].RasterYSize
width[1] = ds[1].RasterXSize
height[1] = ds[1].RasterYSize

temperature_a = np.array([[[0 for i in range(5000)] for j in range(5000)] for k in range(len(sys.argv) - 1)])

for i in range(0, len(ds)):
    temperature_pre = ds[i].GetRasterBand(1).ReadAsArray()
    print('temperature_pre[', i, ']の移し替え')
    for j in range(0, width[0]): 
        for k in range(0, height[0]): 
            temperature_a[i][k][j] = temperature_pre[k][j]
            

gt = [[0 for i in range(6)] for j in range(2)]

#gt_preはオリジナルの座標系のデータ


for i in range(0, 2):
    gt_pre = ds[i].GetGeoTransform()
    print(gt_pre)
    for j in range(0, 6):
        gt[i][j] = gt_pre[j]


miny = [0] * len(ds)
minx = [0] * len(ds)
maxx = [0] * len(ds)
maxy = [0] * len(ds)

for i in range(0, len(ds)): 
    min_max_caluculater(gt, width, height, i)


print('本来の最小', gt[0][0], gt[0][3] + width[0]*gt[0][4] + height[0]*gt[0][5])
print('本来の最大', gt[0][0] + width[0]*gt[0][1] + height[0]*gt[0][2], gt[0][3])
print(minx[0], miny[0])
print(maxx[0], maxy[0])


# outputの時に最大最小値の座標を指定するために使う
op_miny = minimum_caluculation(miny)
op_minx = minimum_caluculation(minx)
op_maxy = maximum_caluculation(maxy)
op_maxx = maximum_caluculation(maxx)


op_width = float_to_int((op_maxx-op_minx)/0.00833)
op_height = float_to_int((op_maxy-op_miny)/0.00833)


op_temperature = np.array([[0.0]*op_width]*op_height)


range_minx = float_to_int((minx[0] - op_minx)/abs(gt[0][1]))
range_maxx = float_to_int((minx[0] - op_minx)/abs(gt[0][1]) + width[0])
range_miny = float_to_int((miny[0] - op_miny)/abs(gt[0][5]))
range_maxy = float_to_int((miny[0] - op_miny)/abs(gt[0][5]) + height[0])

print(range_minx, range_miny)
print(range_maxx, range_maxy)

print("temperature1_aの計算")

for i in range(range_minx, range_maxx): 
    for j in range(range_miny, range_maxy): 
        if -2 < temperature1_a[j - range_miny][i - range_minx] and temperature1_a[j - range_miny][i - range_minx] < 40:
            op_temperature[j][i] = op_temperature[j][i] + temperature1_a[j - range_miny][i - range_minx]
            if op_temperature[j][i] != temperature1_a[j - range_miny][i - range_minx]:
                print(op_temperature[j][i], temperature1_a[j - range_miny][i - range_minx])
                op_temperature[j][i] = op_temperature[j][i] / 2



range_minx = float_to_int((minx[1] - op_minx)/abs(gt[1][1]))
range_maxx = float_to_int((minx[1] - op_minx)/abs(gt[1][1]) + width[1])
range_miny = float_to_int((miny[1] - op_miny)/abs(gt[1][5]))
range_maxy = float_to_int((miny[1] - op_miny)/abs(gt[1][5]) + height[1])


print("temperature2_aの計算")


for k in range(range_minx, range_maxx): 
    for l in range(range_miny, range_maxy): 
        #print(l - range_miny, k - range_minx)
        if -2 < temperature2_a[l - range_miny][k - range_minx] and temperature2_a[l - range_miny][k - range_minx] < 40:
            op_temperature[l][k] = op_temperature[l][k] + temperature2_a[l - range_miny][k - range_minx]
            if op_temperature[l][k] != temperature2_a[l - range_miny][k - range_minx]:
                op_temperature[l][k] = op_temperature[l][k] / 2



print("書き込み中")
dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
band = 1 # バンド数
output = gdal.GetDriverByName('GTiff').Create('/Users/ishizawadaisuke/Desktop/aaa.tif', op_width, op_height, band, dtype) # 空の出力ファイル

output.SetGeoTransform((op_minx, 0.00833, 0, op_maxy, 0, -0.00833)) # 座標系指定
srs = osr.SpatialReference() # 空間参照情報
srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

output.GetRasterBand(1).WriteArray(op_temperature)   # 赤バンド書き出し（b1はnumpy 2次元配列）
output.FlushCache()                     # ディスクに書き出し
elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
output = None  
