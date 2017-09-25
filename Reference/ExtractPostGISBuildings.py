import psycopg2
import psycopg2.extras

# for parsing the polygon strings handed back from the db
import re

conn_string = "host='localhost' dbname='osm' user='mpm2017' password=''"
# print the connection string we will use to connect
print
"Connecting to database\n	->%s" % (conn_string)

conn = psycopg2.connect(conn_string)

# HERE IS THE IMPORTANT PART, by specifying a name for the cursor
# psycopg2 creates a server-side cursor, which prevents all of the
# records from being downloaded at once from the server.
cursor = conn.cursor()
# cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)

cursor.execute('''SELECT osm_id, ST_AsText(ST_Transform(way, 4326))
                        FROM planet_osm_polygon
                        where building is not null and raster is false
                        limit 100''')

# Because cursor objects are iterable we can just call 'for - in' on
# the cursor object and the cursor will automatically advance itself
# each iteration.
# This loop should run 1000 times, assuming there are at least 1000
# records in 'my_table'
row_count = 0

idlist=[]

for row in cursor:

    row_count += 1
    # print("row: %s    %s\n" % (row_count, row)) # prints the whole multipolygon & OSM ID text

    osmid = row[0]  # Get the osm feature id out - to be used later to mark the

    tup = re.search(r"^POLYGON\(\((.*?),.*",row[1]).group(1) # Use regular expression to extract first coordinate

    floats = [float(x) for x in tup.split()]    # use list comprehension to convert 'num num' into [float,float]

    # print(osmid, floats)

    idlist.append([osmid]) # adds the osm id's to a list for the executemany command



# print(idlist)

# runs and update command setting raser=true for each of the osmid's we have retrieved the coordinates for
cursor.executemany(''' UPDATE planet_osm_polygon SET raster = TRUE  WHERE osm_id = %s''', idlist)

conn.commit()


