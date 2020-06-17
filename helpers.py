import os
import sys
import gdal
import numpy as np
import math
from py_snap_helpers import *

def get_slstr_nodata_mask(classif_flags):
    
    # 'unfilled_pixel': 128
    
    b1 = int(math.log(128, 2))
    b2 = b1
    
    return _capture_bits(classif_flags.astype(np.int64), b1, b2)

def get_slstr_confidence_mask(slstr_confidence, classif_flags):
    
    pixel_classif_flags = {'coastline': 1,
                           'cosmetic': 256,
                             'day': 1024,
                             'duplicate': 512,
                             'inland_water': 16,
                             'land': 8,
                             'ocean': 2,
                             'snow': 8192,
                             'spare': 64,
                             'summary_cloud': 16384,
                             'summary_pointing': 32768,
                             'sun_glint': 4096,
                             'tidal': 4,
                             'twilight': 2048,
                             'unfilled': 32}
    
    
    b1 = int(math.log(pixel_classif_flags[slstr_confidence], 2))
    b2 = b1
    
    return _capture_bits(classif_flags.astype(np.int64), b1, b2)

def get_slstr_mask(slstr_cloud, classif_flags):
    
    pixel_classif_flags = {'11_12_view_difference': 2048,
                           '11_spatial_coherence': 64,
                           '1_37_threshold': 2,
                           '1_6_large_histogram': 8,
                           '1_6_small_histogram': 4,
                           '2_25_large_histogram': 32,
                           '2_25_small_histogram': 16,
                           '3_7_11_view_difference': 4096,
                           'fog_low_stratus': 1024,
                           'gross_cloud': 128,
                           'medium_high': 512,
                           'spare': 16384,
                           'thermal_histogram': 8192,
                           'thin_cirrus': 256,
                           'visible': 1}
    
    
    b1 = int(math.log(pixel_classif_flags[slstr_cloud], 2))
    b2 = b1
    
    return _capture_bits(classif_flags.astype(np.int64), b1, b2)


def _capture_bits(arr, b1, b2):
    
    width_int = int((b1 - b2 + 1) * "1", 2)
 
    return ((arr >> b2) & width_int).astype('uint8')

def export_s3(bands):

    ds = gdal.Open(bands[0])
    
    width = ds.RasterXSize
    height = ds.RasterYSize

    input_geotransform = ds.GetGeoTransform()
    input_georef = ds.GetProjectionRef()
    
    ds = None
    
    driver = gdal.GetDriverByName('GTiff')
    
    output = driver.Create('s3.tif', 
                       width, 
                       height, 
                       len(bands), 
                       gdal.GDT_Float32)

    output.SetGeoTransform(input_geotransform)
    output.SetProjection(input_georef)
    
    for index, band in enumerate(bands):
        print(band)
        temp_ds = gdal.Open(band) 
        
        band_data = temp_ds.GetRasterBand(1).ReadAsArray()
        output.GetRasterBand(index+1).WriteArray(band_data)
        
    output.FlushCache()
    
    return True

def read_s3(bands):

    gdal.UseExceptions()
    
    stack = []
    
    for index, band in enumerate(bands):
        
        temp_ds = gdal.Open(band) 
 
        if not temp_ds:
            raise ValueError()
            
        stack.append(temp_ds.GetRasterBand(1).ReadAsArray())
      
    return np.dstack(stack)

