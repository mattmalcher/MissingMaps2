# Script using Functions.py to read in worldpop raster data and OSM raster data generated using genOSMraster.py and
# manipulate it using numpy to compare locations of buildings and people.

from Functions import *   # imports all the functions in Functions.py
import numpy.ma as ma     # imports the tools for creating masked numpy arrays

proj = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'


# Import worldpop tiff
pop_tiff_name = 'Input/155_NPL_ppp_v2c_2015_UNadj/NPL_ppp_v2c_2015_UNadj.tif'
[wp_array,tfm,col_p,row_p] = gt_to_array(pop_tiff_name)
wp_array = ma.masked_equal(wp_array, -999)                          # where wp array=-999 mask it to exclude from calcs
print('WorldPop Array Max: ', wp_array.max(), ' Min: ', wp_array.min())


# Import OSM tiff
osm_tiff_name = 'Output/osm_count.tiff'
[osm_array,tfm,col_o,row_o] = gt_to_array(osm_tiff_name)
osm_array[osm_array == 0] = 0.01                                    # where osm array=0 set it to 0.01
print('OSM Array Max: ', osm_array.max(), ' Min: ', osm_array.min())
array_to_gt(osm_array, osm_tiff_name, tfm, proj)


# Create array of people/buildings
pob_tiff_name = 'Output/pob.tiff'
print('\nCreating People/Buildings (pob) Array')
pob_array = np.divide(wp_array,osm_array)                           # use numpy array operators instead of loops
print('People/Building Array Max: ', pob_array.max(), ' Min: ', pob_array.min())
array_to_gt(pob_array, pob_tiff_name, tfm, proj)


# Create array of log(people/buildings)
log_pob_tiff_name = 'Output/log_pob.tiff'
print('\nCreating Log People/Buildings (log_pob) Array')

pob0 = pob_array
pob0[pob0 < 0.01] = 1.0 # before creating a log array change any values less than 0 to 1 to avoid NaN's

log_pob_array = np.log(pob0)                                        # use numpy array operators instead of loops

print('People/Building Array Max: ', log_pob_array.max(), ' Min: ', log_pob_array.min())
array_to_gt(log_pob_array, log_pob_tiff_name, tfm, proj)


# # Create pop array normalised to sum to 1
# wp_norm_array = np.divide(wp_array,wp_array.sum())
#
#
# osm_norm_array = np.divide(osm_array,osm_array.sum())
#
# log_diff_array=np.log(diff_array)
# print('Diff Array Max: ', diff_array.max(), ' Min: ', diff_array.min())
#
# out_tiff_name= 'Log_Diff_Array.tiff'
# array_to_gt(log_diff_array,out_tiff_name,tfm,proj)
