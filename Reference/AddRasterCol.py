import psycopg2
import psycopg2.extras


conn_string = "host='localhost' dbname='osm' user='mpm2017' password=''"
# print the connection string we will use to connect
print("Connecting to database\n	->%s" % (conn_string))

conn = psycopg2.connect(conn_string)

# HERE IS THE IMPORTANT PART, by specifying a name for the cursor
# psycopg2 creates a server-side cursor, which prevents all of the
# records from being downloaded at once from the server.
cursor = conn.cursor()

print('Creating Ratster Column in planet_osm_polygon. This may take some time...')
cursor.execute('ALTER TABLE planet_osm_polygon ADD COLUMN "raster" boolean DEFAULT false')

conn.commit() # commit changes to db




