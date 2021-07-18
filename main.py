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


def minimum_caluculation(min, len) -> float: #現状ね、
    a = min[0]
    for i in range(0, len): 
        if a > min[i]: 
            a = min[i]
    
    return a

def maximum_caluculation(max, len) -> float: #現状ね、
    a = max[0]
    for i in range(0, len): 
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


def width_height_inserter(ds_num, width_num, height_num, i): 
    width_num[i] = ds_num[i].RasterXSize
    height_num[i] = ds_num[i].RasterYSize


# tifファイルを開く
start = time.time()
ds = [0] * (len(sys.argv) - 2)

for i in range(0, len(sys.argv) - 2): 
    print('ds[', i, ']をオープン')
    ds[i] = gdal.Open(sys.argv[i + 1])

old_cs= osr.SpatialReference()
old_cs.ImportFromWkt(ds[0].GetProjectionRef())
old_cs.ImportFromWkt(ds[1].GetProjectionRef())


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


#widthとheightの宣言、代入
width = [0] * len(ds)
height = [0] * len(ds)

for i in range(0, len(ds)): 
    width_height_inserter(ds, width, height, i)

temperature_a = np.array([[[0.0 for i in range(3000)] for j in range(3000)] for k in range(len(sys.argv) - 1)])

for i in range(0, len(ds)):
    temperature_pre = ds[i].GetRasterBand(1).ReadAsArray()
    print('temperature_pre[', i, ']の移し替え')
    for j in range(0, width[i]): 
        for k in range(0, height[i]): 
            temperature_a[i][k][j] = temperature_pre[k][j]
            

gt = [[0 for i in range(6)] for j in range(len(ds))]

#gt_preはオリジナルの座標系のデータ


for i in range(0, len(ds)):
    gt_pre = ds[i].GetGeoTransform()
    print(gt_pre)
    for j in range(0, 6):
        gt[i][j] = gt_pre[j]


miny = [0.0] * len(ds)
minx = [0.0] * len(ds)
maxx = [0.0] * len(ds)
maxy = [0.0] * len(ds)

for i in range(0, len(ds)): 
    min_max_caluculater(gt, width, height, i)


print('本来の最小', gt[0][0], gt[0][3] + width[0]*gt[0][4] + height[0]*gt[0][5])
print('本来の最大', gt[0][0] + width[0]*gt[0][1] + height[0]*gt[0][2], gt[0][3])
print(minx[0], miny[0])
print(maxx[0], maxy[0])


# outputの時に最大最小値の座標を指定するために使う
op_miny = minimum_caluculation(miny, len(ds))
op_minx = minimum_caluculation(minx, len(ds))
op_maxy = maximum_caluculation(maxy, len(ds))
op_maxx = maximum_caluculation(maxx, len(ds))


op_width = float_to_int((op_maxx-op_minx)/0.00833)
op_height = float_to_int((op_maxy-op_miny)/0.00833)

op_temperature = np.array([[0.0 for i in range(op_width)] for j in range(op_height)])

print(op_width, op_height)

for i in range(0, len(ds)): 
    print('temperature_a', i, 'の計算中')

    range_minx = float_to_int((minx[i] - op_minx)/abs(gt[i][1]))
    range_maxx = float_to_int((minx[i] - op_minx)/abs(gt[i][1]) + width[i])
    range_miny = float_to_int((miny[i] - op_miny)/abs(gt[i][5]))
    range_maxy = float_to_int((miny[i] - op_miny)/abs(gt[i][5]) + height[i])

    for j in range(range_minx, range_maxx): 
        for k in range(range_miny, range_maxy):
            if -2 < temperature_a[i][k - range_miny][j - range_minx] and temperature_a[i][k - range_miny][j - range_minx] < 40:
                op_temperature[k][j] = op_temperature[k][j] + temperature_a[i][k - range_miny][j - range_minx]
                if op_temperature[k][j] != temperature_a[i][k - range_miny][j - range_minx]:
                    op_temperature[k][j] = op_temperature[k][j] / 2



print("書き込み中")
dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
band = 1 # バンド数
output = gdal.GetDriverByName('GTiff').Create(sys.argv[len(sys.argv) - 1], op_width, op_height, band, dtype) # 空の出力ファイル

output.SetGeoTransform((op_minx, 0.00833, 0, op_maxy, 0, -0.00833)) # 座標系指定
srs = osr.SpatialReference() # 空間参照情報
srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

output.GetRasterBand(1).WriteArray(op_temperature)   # 赤バンド書き出し（b1はnumpy 2次元配列）
output.FlushCache()                     # ディスクに書き出し
elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
output = None  
