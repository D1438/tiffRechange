from osgeo import osr, gdal



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



# tifファイルを開く
ds = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-01-02.tif')
old_cs= osr.SpatialReference()
old_cs.ImportFromWkt(ds.GetProjectionRef())

temperature1 = ds.GetRasterBand(1)
temperature1_a = temperature1.ReadAsArray()

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

#gt_preはオリジナルの座標系のデータ
gt_pre = ds.GetGeoTransform()

#gtはgt_preを小数点第５位で切り落とした座標系のデータをgt_preの配列の個数分宣言した
gt = [0] * len(gt_pre)
for j in range(0, len(gt_pre)): 
    if gt_pre[j] < 0 :
        gt[j] = round(float(gt_pre[j]), 5)
    else :
        gt[j] = round(float(gt_pre[j]), 5)

print(gt)

miny = normalize(gt[5], gt[3] + width*gt[4] + height*gt[5])
minx = normalize(gt[1], gt[0])
maxx = normalize(gt[1], gt[0] + width*gt[1] + height*gt[2])
maxy = normalize(gt[5], gt[3])


#get the coordinates in lat long
minlatlong = transform.TransformPoint(minx, miny)
maxlatlong = transform.TransformPoint(maxx, maxy)
print(minlatlong, maxlatlong)


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