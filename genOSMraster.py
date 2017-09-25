# Script using Functions.py to connect to the PostGIS database created using osm2pgsql and create a raster of
# OSM building density

from Functions import *   #imports all the functions in Functions.py

# Set up the connection to the database which contains the OSM data for our region of interest
[cur, conn] = init_db()

# Read in the worldpop geotiff and get the dimensions and transform
pop_tiff_name = 'Input/155_NPL_ppp_v2c_2015_UNadj/NPL_ppp_v2c_2015_UNadj.tif'
[wp_array,tfm,col,row] = gt_to_array(pop_tiff_name)

print('WorldPop Array Max: ', wp_array.max(), ' Min: ', wp_array.min())

# Create a blank array to contain osm building count
blank_array = np.zeros((row, col))

# use the osm_db_count function from Functions.py to iterate over the items in the
# postGIS database and build up a raster
osm_array = osm_db_count(cur, conn, blank_array, tfm)

# print out basic stats about the OSM array for sanity checking and setting scales in QGIS
print('OSM Array Max: ', osm_array.max(), ' Min: ', osm_array.min())

# Write out OSM array to a new geotiff matching the spec of the worldpop tiff
out_tiff_name= 'Output/osm_count.tiff'
proj = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
array_to_gt(osm_array, out_tiff_name, tfm, proj)

print('Done!')
