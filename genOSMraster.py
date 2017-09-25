from Functions import *

# Set up the connection to the database which contains the OSM data for our region of interest
[cur, conn] = init_db()

# Read in the worldpop geotiff and get the dimensions and transform
pop_tiff_name = 'Input/155_NPL_ppp_v2c_2015_UNadj/NPL_ppp_v2c_2015_UNadj.tif'
[wp_array,tfm,col,row] = gt_to_array(pop_tiff_name)

print('WorldPop Array Max: ', wp_array.max(), ' Min: ', wp_array.min())

# Create a blank array to contain osm building count
# blank_array = [[0 for i in range(col)] for j in range(row)]
blank_array = np.zeros((row, col))

osm_array = osm_db_count(cur, conn, blank_array, tfm)

print('OSM Array Max: ', osm_array.max(), ' Min: ', osm_array.min())

# Write out OSM array to a new geotiff matching the spec of the worldpop tiff
out_tiff_name= 'Output/osm_count.tiff'
proj = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
array_to_gt(osm_array, out_tiff_name, tfm, proj)

print('Done!')
