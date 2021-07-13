from osgeo import osr, gdal

# 座標を各解像度の値に一番近い値に変換する
def normalize(resolution, parameter, i): 

    while i < 180:
        now = abs(parameter - i)
        previous = abs(parameter - i - abs(resolution))
        #print(now, previous)

        if now > previous: 
            answer = i
        i = i + abs(resolution)

    a = 0
    return answer

# get the existing coordinate system
ds = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-01-02.tif')
old_cs= osr.SpatialReference()
old_cs.ImportFromWkt(ds.GetProjectionRef())

# create the new coordinate system
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


# create a transform object to convert between coordinate systems
transform = osr.CoordinateTransformation(old_cs,new_cs) 

#get the point to transform, pixel (0,0) in this case
width = ds.RasterXSize
height = ds.RasterYSize

#gt_preはオリジナルの座標系のデータ
gt_pre = ds.GetGeoTransform()

#gtはgt_preを小数点第５位で切り落とした座標系のデータ
gt = [0] * len(gt_pre)
for j in range(0, len(gt_pre)): 
    #print(gt_pre[j])
    if gt_pre[j] < 0 :
        gt[j] = round(float(gt_pre[j]), 5)
    else :
        gt[j] = round(float(gt_pre[j]), 5)

print(gt)
minx = round(gt[0], 5)
miny = round(gt[3] + width*gt[4] + height*round(-1*gt[5], 5)*-1, 5)
maxx = round(gt[0] + width*round(gt[1], 5) + height*gt[2], 5)
maxy = round(gt[3], 5)

a = 0

miny1 = round(normalize(gt[5], miny, a), 5)
minx1 = round(normalize(gt[1], minx, a), 5)
maxx1 = round(normalize(gt[1], maxx, a), 5)
maxy1 = round(normalize(gt[5], maxy, a), 5)


#get the coordinates in lat long
minlatlong = transform.TransformPoint(minx1, miny1) 
maxlatlong = transform.TransformPoint(maxx1, maxy1)

print(minlatlong)
print(maxlatlong)
print(width)
print(height)


