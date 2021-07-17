from osgeo import osr, gdal
import math
import numpy as np
import time

# 座標を各解像度の値に一番近い値に変換する
def normalize(resolution, parameter): 
    i = 0

    while i < 180:
        now = abs(parameter - i)
        previous = abs(parameter - i - abs(resolution))

        if now > previous: 
            answer = i
        i = i + abs(resolution)
    
    return round(answer, 5)


def rounder(gt_array, pre_array): 
    for j in range(0, len(pre_array)): 
       if pre_array[j] < 0 :
          gt_array[j] = round(float(pre_array[j]), 5)
       else :
          gt_array[j] = round(float(pre_array[j]), 5)

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


# tifファイルを開く
start = time.time()
ds = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-01-02.tif')
ds1 = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-01-13.tif')
old_cs= osr.SpatialReference()
old_cs.ImportFromWkt(ds.GetProjectionRef())
old_cs.ImportFromWkt(ds1.GetProjectionRef())

temperature1_a = ds.GetRasterBand(1).ReadAsArray()
temperature2_a = ds1.GetRasterBand(1).ReadAsArray()


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

width[0] = ds.RasterXSize
height[0] = ds.RasterYSize
width[1] = ds1.RasterXSize
height[1] = ds1.RasterYSize

#gt_preはオリジナルの座標系のデータ
gt_pre = ds.GetGeoTransform()
gt1_pre = ds1.GetGeoTransform()

#gtはgt_preを小数点第５位で切り落とした座標系のデータをgt_preの配列の個数分宣言した
gt = [0] * len(gt_pre)
gt1 = [0] * len(gt1_pre)
miny = [0] * 2
minx = [0] * 2
maxx = [0] * 2
maxy = [0] * 2
rounder(gt, gt_pre)
rounder(gt1, gt1_pre)


miny[0] = normalize(gt[5], gt[3] + width[0]*gt[4] + height[0]*gt[5])
minx[0] = normalize(gt[1], gt[0])
maxx[0] = normalize(gt[1], gt[0] + width[0]*gt[1] + height[0]*gt[2])
maxy[0] = normalize(gt[5], gt[3])

miny[1] = normalize(gt1[5], gt1[3] + width[0]*gt1[4] + height[0]*gt1[5])
minx[1] = normalize(gt1[1], gt1[0])
maxx[1] = normalize(gt1[1], gt1[0] + width[0]*gt1[1] + height[0]*gt1[2])
maxy[1] = normalize(gt1[5], gt1[3])



# outputの時に最大最小値の座標を指定するために使う
op_miny = minimum_caluculation(miny)
op_minx = minimum_caluculation(minx)
op_maxy = maximum_caluculation(maxy)
op_maxx = maximum_caluculation(maxx)


op_width = float_to_int((op_maxx-op_minx)/0.00833)
op_height = float_to_int((op_maxy-op_miny)/0.00833)

op_temperature = np.array([[0.0]*op_width]*op_height)


#print(op_maxx - abs(minx[0]/0.00833-op_minx/0.00833))
range_minx = int((minx[0] - op_minx)/0.00833)
range_maxx = int((minx[0] - op_minx)/0.00833 + width[0])
range_miny = int((miny[0] - op_miny)/0.00833)
range_maxy = int((miny[0] - op_miny)/0.00833 + height[0])

print("temperature1_aの計算")
for i in range(range_minx, range_maxx): 
    for j in range(range_miny, range_maxy): 
        if -2 < temperature1_a[j - range_miny][i - range_minx] and temperature1_a[j - range_miny][i - range_minx] < 40:
            op_temperature[j][i] = op_temperature[j][i] + temperature1_a[j - range_miny][i - range_minx]
            if op_temperature[j][i] != temperature1_a[j - range_miny][i - range_minx]:
                print(op_temperature[j][i], temperature1_a[j - range_miny][i - range_minx])
                op_temperature[j][i] = op_temperature[j][i] / 2



range_minx = int((minx[1] - op_minx)/0.00833)
range_maxx = int((minx[1] - op_minx)/0.00833 + width[1])
range_miny = int((miny[1] - op_miny)/0.00833)
range_maxy = int((miny[1] - op_miny)/0.00833 + height[1])


print("temperature2_aの計算")
for k in range(range_minx, range_maxx): 
    for l  in range(range_miny, range_maxy): 
        if -2 < temperature2_a[l - range_miny][k - range_minx] and temperature2_a[l - range_miny][k - range_minx] < 40:
            op_temperature[l][k] = op_temperature[l][k] + temperature2_a[l - range_miny][k - range_minx]
            if op_temperature[l][k] != temperature2_a[l - range_miny][k - range_minx]:
                op_temperature[l][k] = op_temperature[l][k] / 2



#get the coordinates in lat long
minlatlong = transform.TransformPoint(minx[0], miny[0])
maxlatlong = transform.TransformPoint(maxx[0], maxy[0])
minlatlong1 = transform.TransformPoint(minx[1], miny[1])
maxlatlong1 = transform.TransformPoint(maxx[1], maxy[1])


op_minlatlong = transform.TransformPoint(op_minx, op_miny)
op_maxlatlong = transform.TransformPoint(op_maxx, op_maxy)


#print(minlatlong, maxlatlong)
#print(minlatlong1, maxlatlong1)
#print(op_minlatlong, op_maxlatlong)


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
