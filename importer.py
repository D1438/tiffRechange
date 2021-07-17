import osgeo
from osgeo import osr, gdal
import numpy as np
import sys
from sys import argv


ds1 = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-08-13.tif', gdal.GA_ReadOnly)
ds2 = gdal.Open('/Users/ishizawadaisuke/Documents/graduate/temperture/ORD改変/04-01-13.tif', gdal.GA_ReadOnly)


