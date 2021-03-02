# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 15:19:55 2020
Functions used to clip the HySpex raw data and IMUGPS data based on user-defined extent
@author: Ting Zheng, tzheng39@wisc.edu
"""

import numpy as np
import json,os,logging

# Test:
# raw_imugps_file = r'Z:\townsenduser-rw\hyspex_raw\2019\20190711\CHEESEHEAD-2_20190711' + '/CHEESEHEAD-2_20190711_05_SWIR_384_SN3142_FOVx2_raw.txt'    
# clipped_imugps_file = r'Z:\townsenduser-rw\hyspex_raw\2019\20190711\CHEESEHEAD-2_20190711' + '/CHEESEHEAD-2_20190711_05_clipped.txt'    
# raw_image_file = r'Z:\townsenduser-rw\hyspex_raw\2019\20190711\CHEESEHEAD-2_20190711' + '/CHEESEHEAD-2_20190711_05_SWIR_384_SN3142_FOVx2_raw.hyspex'    
# clipped_image_file = r'Z:\townsenduser-rw\hyspex_raw\2019\20190711\CHEESEHEAD-2_20190711' + '/CHEESEHEAD-2_20190711_05_clipped.hyspex'    

# # map_extent = [45.90066,45.98553,-90.34544,-90.20833]
# map_shape = r'E:\HyspexPro_CHTC' + '\CH_extent.shp'
# End of test
logger = logging.getLogger(__name__)

def extent_determination(raw_imugps_file,map_shape,buffer=0):
    """ determine the range of raw image falls inside the map_extent
        Arguments:
        raw_imugps_file: str
            Raw IMUGPS filename.
        map_shape: str
            filename for the map extent shapefile (must be in EPSG:4326)
        buffer: int
            buffer size in lines, default = 0 (keep 0 lines outside of the extent)
 
    """  
        
    from osgeo import ogr
    from shapely.geometry import Point,Polygon,MultiPoint,shape
    
    
    
    # Read the shp file and extract the geometry info:
    file = ogr.Open(map_shape)    
    extent_shp = file.GetLayer(0)
    # Get the first feature of the layer:
    feature = extent_shp.GetFeature(0)
    feature_json = feature.ExportToJson()
    feature_dict = json.loads(feature_json)         
    
    # Convert to shapely geometry:
    map_geom = shape(feature_dict['geometry'])
    map_poly = Polygon(map_geom)    

        
    # Load raw IMU/GPS data, convert lat/lon to line geometry:
    raw_imugps = np.loadtxt(raw_imugps_file)

    # Construct line object based on raw_imugps
    line_coord = list(zip(raw_imugps[:,1].flatten(),raw_imugps[:,2].flatten()))
    flight_line = MultiPoint([Point(line_coord[i]) for i in range(0,len(line_coord))]) 
    # Intersect the extent polygon with the line_coord:
    line_in = np.array([ i for i in range(0,len(line_coord)) if flight_line[i].within(map_poly)])    
    
    # testing:
        
    # test = line_in[1:] - line_in[0:(len(line_in)-1)]   
    
    # Check if the flight line is inside the ROI: 
    if line_in.size == 0:
        l_start = -1
        l_end = -1
    else:            
        # return the row range:
        if (min(line_in)-buffer)>0:
            l_start = raw_imugps[min(line_in)-buffer][0]
        else:
            l_start = 1
        
        if (max(line_in)+buffer)< len(line_coord):
            l_end = raw_imugps[max(line_in)+buffer][0]
        else:
            l_end = len(line_coord)
    
    return int(l_start),int(l_end)


def clip_imugps(raw_imugps_file,map_shape,clipped_imugps_file):
    """ clip the imugps data based on given extent
    Arguments:
    raw_imugps_file: str
        Raw IMUGPS filename.
    l_start: int
        The starting line.
    l_end: int
        The endding line.
    clipped_imugps_file: str
        Clipped IMUGPS filename
    """
    # define a clip_tag to check if the flight line is inside the ROI
    clip_tag = 1
    if os.path.exists(clipped_imugps_file):
        logger.info('Write the clipped imugps data to %s.' %clipped_imugps_file)
        return clip_tag
    
    
    l_start,l_end = extent_determination(raw_imugps_file,map_shape)
    if (l_start == -1) or (l_end == -1):
        logger.info('Flightline %s is outside of the ROI.' %raw_imugps_file)
        clip_tag = 0
        return clip_tag
    raw_imugps = np.loadtxt(raw_imugps_file)
    
    # Clip the data
    s = l_start - 1
    clipped_imugps = raw_imugps[s:l_end]
    
    # Write the clipped file to disk:
    np.savetxt(clipped_imugps_file,clipped_imugps)
    
    logger.info('Write the clipped imugps data to %s.' %clipped_imugps_file)
    
    return clip_tag
    
    
def clip_hyspex(raw_image_file,clipped_image_file,clipped_imugps_file):    
    """ clip the raw hyspex data based on given extent
    Arguments:
    raw_image_file: str
        Raw hyspex filename.
    l_start: int
        The starting line.
    l_end: int
        The endding line.
    clipped_image_file: str
        Clipped hyspex image filename
    """
    
    if os.path.exists(clipped_image_file):
        logger.info('Write the clipped image to %s.' %clipped_image_file)
        return
 
    from ENVI  import  read_envi_header, write_envi_header
    
    # Load the clipped imugps file:
    clipped_imugps = np.loadtxt(clipped_imugps_file)
    l_start = int(clipped_imugps[0,0])
    l_end = int(clipped_imugps[-1,0])
    
    
    # Read DN image.
    dn_header = read_envi_header(os.path.splitext(raw_image_file)[0]+'.hdr')
    dn_image = np.memmap(raw_image_file,
                         dtype='uint16',
                         mode='r',
                         offset=dn_header['header offset'],
                         shape=(dn_header['lines'],
                                dn_header['bands'],
                                dn_header['samples']))



    # read the metadata from the raw image:
    lines_raw = dn_header['lines']    
    offset = dn_header['header offset']    
    fid_r = open(raw_image_file, 'rb')
    fid_w = open(clipped_image_file, 'wb')
    temp = fid_r.read(offset)
    fid_w.write(temp)
    fid_r.close()
      
    

    # Set up the start line and the end line:
    s = l_start - 1
    total_lines = int(l_end - s)   
    # Adjust the file pointer position:
    fid_w.seek(dn_header['header offset'],0)    
    
    for from_line in range(s, l_end, 500):


        # Determine chunck size.
        to_line = min(from_line+500, l_end)
  
        clipped = dn_image[from_line:to_line,:,:]
        # Write clipped data to the file.
        fid_w.write(clipped.tostring())

        # Clear temporary data.
        del clipped,to_line
    fid_w.close()


    # Clear data.
    dn_image.flush()
    del dn_image
    
    # Write header.
    clipped_header = dn_header
    clipped_header['clip tag'] = 1
    clipped_header['starting line'] = l_start
    clipped_header['ending line'] = l_end
    clipped_header['lines'] = total_lines
    clipped_header['original lines'] = lines_raw
    

    write_envi_header(os.path.splitext(clipped_image_file)[0]+'.hdr', clipped_header)
    del clipped_header, dn_header    
    logger.info('Write the clipped image to %s.' %clipped_image_file)

        
        
        
