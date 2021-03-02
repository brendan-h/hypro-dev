"""
This script is used to create shapefile based on input IGM  
Usage: python create_flightline_shape.py -id Z:/townsenduser-rw/HyspexPro/Output/Cheesehead/CHEESE_20190806_P2 -od Z:/townsenduser-rw/HyspexPro/Output/Cheesehead/CHEESE_20190806_P2

"""
import os,glob,argparse,sys
import numpy as np
from osgeo import gdal, ogr, osr
from ENVI import read_envi_header

def create_polygon(dir_in,outshp):
    if os.path.exists(outshp):
        print("Output file exists!")
        sys.exit(1)

    # Read IGM.
    igm_header = read_envi_header(glob.glob(dir_in+'*IGM.hdr')[0])
    igm_image = np.memmap(glob.glob(dir_in+'*IGM')[0],
                          dtype='float64',
                          mode='r',
                          offset=0,
                          shape=(2, igm_header['lines'], igm_header['samples']))
    lon = igm_image[0,:,:]
    lat = igm_image[1,:,:]
    igm_image.flush()
    del igm_image

    # concat outline lon points:
    # lons = list(lon[:,0].flatten()) +list(lon[-1,:].flatten()) + list(np.flip(lon[:,-1].flatten()))+  list(np.flip(lon[0,:].flatten()))
    lons = np.concatenate((lon[:,0].flatten(),lon[-1,:].flatten(),np.flip(lon[:,-1].flatten()),np.flip(lon[0,:].flatten())))
    # lats = list(lat[:,0].flatten()) +list(lat[-1,:].flatten()) + list(np.flip(lat[:,-1].flatten()))+  list(np.flip(lat[0,:].flatten()))
    lats = np.concatenate((lat[:,0].flatten(),lat[-1,:].flatten(),np.flip(lat[:,-1].flatten()),np.flip(lat[0,:].flatten())))
    
    # construct the geometry:
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for i in range(0,len(lons)):
        ring.AddPoint(lons[i],lats[i])

    # Create polygon
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly.ExportToWkt()

def write_shapefile(poly, dir_in,outshp, filename):

    # Open the dem file to import georeference:
    src_ds = gdal.Open(glob.glob(dir_in+'*DEM')[0])

    if src_ds is None:
        print (('Unable to open DEM for %s') %filename )
        sys.exit(1)



    # Now convert it to a shapefile with OGR    
    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(outshp)
    srs = osr.SpatialReference()
    srs.ImportFromWkt( src_ds.GetProjectionRef() )
    layer = ds.CreateLayer(filename, srs,ogr.wkbPolygon )
    # Add one attribute
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTString))
    defn = layer.GetLayerDefn()

    ## If there are multiple geometries, put the "for" loop here

    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)
    feat.SetField('id', filename)

    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkt(poly)
    feat.SetGeometry(geom)

    layer.CreateFeature(feat)
    feat = geom = None  # destroy these

    # Save and close everything
    ds = layer = feat = geom = None

def main():
    parser = argparse.ArgumentParser(description = "Create shapefile for Hyspex flightlines")
    parser.add_argument("-id", help="Input directory",required=True, type = str)
    parser.add_argument("-od", help="Output directory for all resulting products", required=True, type = str)
    args = parser.parse_args()

    # Get all subdirectories inside the input directory
    sub_dir_ls = glob.glob(args.id + '/*/')

    for sub in sub_dir_ls:
        filename =  os.path.basename(os.path.dirname(sub))
        print('now processing '+ filename)
        # construct the directory for DEM and IGM data (both vnir and swir folder will work):
        dir_in = sub + 'vnir/'
        # Name and directory for the output shp:
        outshp = args.od +'/' + filename +'.shp'
        poly = create_polygon(dir_in,outshp)
        write_shapefile(poly,dir_in,outshp,filename)
        

        



   

if __name__ == "__main__":
    #coords = [(-106.6472953, 24.0370137), (-106.4933356, 24.05293569), (-106.4941789, 24.01969175), (-106.4927777, 23.98804445), (-106.4922614, 23.95582128), (-106.4925834, 23.92302327), (-106.4924068, 23.89048039), (-106.4925695, 23.85771361), (-106.4932479, 23.82457675), (-106.4928676, 23.7922049), (-106.4925072, 23.75980241), (-106.492388, 23.72722475), (-106.4922574, 23.69464296), (-106.4921181, 23.6620529), (-106.4922734, 23.62926733), (-106.4917201, 23.59697561), (-106.4914134, 23.56449628), (-106.4912558, 23.5319045), (-106.491146, 23.49926362), (-106.4911734, 23.46653561), (-106.4910181, 23.43392476), (-106.4910156, 23.40119976), (-106.4909501, 23.3685223), (-106.4908165, 23.33586566), (-106.4907735, 23.30314904), (-106.4906954, 23.27044931), (-106.4906366, 23.23771759), (-106.4905894, 23.20499124), (-106.4905432, 23.17226022), (-106.4904748, 23.1395177), (-106.4904187, 23.10676788), (-106.4903676, 23.07401321), (-106.4903098, 23.04126832), (-106.4902512, 23.00849426), (-106.4901979, 22.97572025), (-106.490196, 22.97401001), (-106.6481193, 22.95609832), (-106.6481156, 22.95801668), (-106.6480697, 22.99082052), (-106.6480307, 23.02362441), (-106.6479937, 23.0563977), (-106.6479473, 23.0891833), (-106.647902, 23.12196713), (-106.6478733, 23.15474057), (-106.6478237, 23.18750353), (-106.6477752, 23.22026138), (-106.6477389, 23.25302505), (-106.647701, 23.28577123), (-106.6476562, 23.31851549), (-106.6476211, 23.3512557), (-106.6475745, 23.38397935), (-106.6475231, 23.41671055), (-106.6474863, 23.44942382), (-106.6474432, 23.48213255), (-106.6474017, 23.51484861), (-106.6474626, 23.54747418), (-106.647766, 23.57991134), (-106.6482374, 23.61220905), (-106.6484783, 23.64467084), (-106.6482308, 23.6775148), (-106.6479338, 23.7103854), (-106.6478395, 23.74309074), (-106.6472376, 23.77618646), (-106.6472982, 23.80876072), (-106.647127, 23.84151129), (-106.6471277, 23.8741312), (-106.6473995, 23.90656505), (-106.6473138, 23.93916488), (-106.6473408, 23.97172031), (-106.6473796, 24.00435261), (-106.6472953, 24.0370137)]
    #out_shp = r'X:\temp\polygon.shp'
    main()