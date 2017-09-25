from __future__ import division # use python3 division behaviour when running on python 2.x
from osgeo import gdal
import math
import numpy as np
import psycopg2
import psycopg2.extras
import re # for parsing the polygon strings handed back from the db

def init_db():

    conn_string = "host='localhost' dbname='osm' user='mpm2017' password=''"

    # print the connection string we will use to connect
    print("Connecting to database\n	->%s" % (conn_string))

    # create database connection & cursor
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    return cursor,conn


def array_to_gt(array,filename,transform,projection):
    # take array and save it as a geotiff with the appropriate transform

    driver = gdal.GetDriverByName('GTiff')

    dataset = driver.Create(
        filename,
        len(array[0]),
        len(array),
        1,
        gdal.GDT_Float32, )

    dataset.SetGeoTransform(transform)
    dataset.SetProjection(projection)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()


def add_raster_col(cursor,conn):

    print('Creating Ratster Column in planet_osm_polygon. This may take some time...')
    cursor.execute('ALTER TABLE planet_osm_polygon ADD COLUMN "raster" boolean DEFAULT false')

    conn.commit()  # commit changes to db


def gt_to_array(filename):
    # Read in geotiff and its properties

    # Set GeoTiff driver
    driver = gdal.GetDriverByName("GTiff")
    driver.Register()

    #Open raster and read number of rows, columns, bands
    dataset = gdal.Open(filename)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    print('\n Input Raster Size: '+ str(rows) + ' rows by '+str(cols)+' cols')

    # https://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file
    # get geotiff spec
    tfm = dataset.GetGeoTransform()

    minx = tfm[0]
    miny = tfm[3] + rows*tfm[4] + cols*tfm[5]
    maxx = tfm[0] + rows*tfm[1] + cols*tfm[2]
    maxy = tfm[3]

    print('Raster Transform: ', tfm)

    allBands = dataset.RasterCount
    band = dataset.GetRasterBand(1)

    band.SetNoDataValue(0)  # Set data value when there is no information

    #raster image as a list of lists
    rasterarray = band.ReadAsArray(0,0,cols,rows)

    return rasterarray,tfm,cols,rows


def osm_db_count(cursor, conn, raster, transform):


    # PostGIS query resulting in iterable object containing data
    cursor.execute('''SELECT osm_id, ST_AsText(ST_Transform(way, 4326))
                            FROM planet_osm_polygon
                            where building is not null and raster is false''')
                            # limit 100000''')

    # n.b. limit here is set to avoid monolithic sql queries - chunked approach is less resource intensive

    # print a descriptive message if there is nothing returned in the cursor.
    if cursor.rowcount == 0:
        print('postGIS Query Result Empty')


    # initialise list of osm_id's - used for updating raster column
    # idlist = []
    building_count=0
    building_outside=0

    for row in cursor:

        # print("row: %s    %s\n" % (row_count, row)) # for debug prints the whole multipolygon & OSM ID text

        osmid = row[0]  # Get the osm feature id out - to be used later to mark the

        tup = re.search(r".*POLYGON\({2,3}(.*?),.*", row[1]).group(1)  # Use regular expression to extract first coordinate,
        # note that the object returned can be either of the form POLYGON((long lat, or MULTIPOLYGON(((long lat,

        floats = [float(x) for x in tup.split()]  # use list comprehension to convert 'num num' into [float,float]
        # long,lat

        # print(osmid, floats)

        # idlist.append([osmid])  # adds the osm id's to a list for the executemany command

        # Offset & scale lat/long, then round down to get appropriate pixel in raster.
        c = int(math.floor((floats[0] - transform[0]) / transform[1])) # Column is Longitude (East-West)
        r = int(math.floor((floats[1] - transform[3]) / transform[5])) # Row is Latitude (North-South)

        # print(r,c)
        try:
            raster[r][c] += 1
            building_count += 1

        except IndexError:
            building_outside += 1

    # print(idlist)
    print('Buildings Counted: ', building_count)
    print('Buildings Outside Raster Area: ',building_outside)

    # runs and update command setting raser=true for each of the osmid's we have retrieved the coordinates for
    # cursor.executemany(''' UPDATE planet_osm_polygon SET raster = TRUE  WHERE osm_id = %s''', idlist)

    # write key indicating rasterised to db
    # print('Marking Rasterised Entries ... ')
    # conn.commit()

    return raster


