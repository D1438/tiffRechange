from osgeo import osr, gdal
import math



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
ds = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-01-02.tif')
ds1 = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-02-14.tif')
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
width = ds.RasterXSize
height = ds.RasterYSize
width1 = ds1.RasterXSize
height1 = ds1.RasterYSize

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


miny[0] = normalize(gt[5], gt[3] + width*gt[4] + height*gt[5])
minx[0] = normalize(gt[1], gt[0])
maxx[0] = normalize(gt[1], gt[0] + width*gt[1] + height*gt[2])
maxy[0] = normalize(gt[5], gt[3])

miny[1] = normalize(gt1[5], gt1[3] + width*gt1[4] + height*gt1[5])
minx[1] = normalize(gt1[1], gt1[0])
maxx[1] = normalize(gt1[1], gt1[0] + width*gt1[1] + height*gt1[2])
maxy[1] = normalize(gt1[5], gt1[3])

# outputの時に指定するために使う
op_miny = minimum_caluculation(miny)
op_minx = minimum_caluculation(minx)
op_maxy = maximum_caluculation(maxy)
op_maxx = maximum_caluculation(maxx)

op_width = float_to_int((op_maxx-op_minx)/0.00833)
op_height = float_to_int((op_maxy-op_miny)/0.00833)


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



"""
dtype = gdal.GDT_Float32 #others: gdal.GDT_Byte, ...
band = 1 # バンド数
output = gdal.GetDriverByName('GTiff').Create('/Users/ishizawadaisuke/Desktop/aaa.tif', width, height, band, dtype) # 空の出力ファイル

output.SetGeoTransform((minx, 0.00833, 0, maxy, 0, -0.00833)) # 座標系指定
srs = osr.SpatialReference() # 空間参照情報
srs.ImportFromEPSG(4326) # WGS84 UTM_48nに座標系を指定
output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

output.GetRasterBand(1).WriteArray(temperature1_a)   # 赤バンド書き出し（b1はnumpy 2次元配列）
output.FlushCache()                     # ディスクに書き出し
output = None  
"""