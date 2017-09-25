#Where the Maps are Missing 2

## Intro
The point of this document is to describe what the tools in this repository are, 
why they are built the way they are and how to use them.

### What are these tools?
These tools take spatial world population data in raster form from[worldpop](http://www.worldpop.org.uk)and locations of building vector data from[open street map](https://www.openstreetmap.org)and compare the two.
The idea is that this provides an indication of where there are people but no maps or 'where the maps are missing'.

The tools in this repository are a development of work done by Simon B. Johnson at the British Red Cross. Please see his 
[Medium post](https://medium.com/@Simon_B_Johnson/where-are-the-maps-missing-b22ceedb26f3#.l8rzisyu1)
and
[GitHub repository](https://github.com/SimonbJohnson/missingmaps_whatsmissing)
for context and a nice write-up of the original project.

### Why have they been made?

Many of the places where disasters occur are 'missing' from the map. 
 [Missing Maps](http://www.missingmaps.org) is a project to give first responders the information they need to assist 
 people effectively. 
 
 Simon has many other responsibilities. As such, updating the tools used for the original blog post has 
fallen somewhere down the list

### What is Next?
As per Simon's original post there are several areas for improvement.
* Investigate more than just buildings
* Creating more intelligent feedback on when to trust World Pop data in well mapped areas
* Create aggregated/fuzzy views to account for World Pop noise and allow easier exploring
* Create maps for all possible countries

Further to these goals it is also important to make the tool more accessible so that it can be leveraged to inform future
mapping efforts.

### How can I use the tools as they exist today?

The rest of this document describes the steps to go through to use these tools to produce maps. The intent is to give the
end user an idea of how everything hangs together, not to provide an all encompassing prescriptive set of instructions.

I worked on this project using macOS and the information below reflects this. However all of the key tools used are cross
platform and there should be no significant barrier to getting this all working on windows or linux.

The key components used are as listed:
* PosgreSQL 9.6.5
* PGadmin3 1.22.2 (PGadmin4 had problems)
* Python 3.6.2 (though should work with 2.x)
* osm2pgsql 0.92.1
* gdal2 2.2.1_3
* gdal2-python 2.2.1_1
* QGIS 2.18

## 1) Setting up PostGIS
[PostGIS](http://www.postgis.org) is an extension for the[PostgreSQL](https://www.postgresql.org) relational database 
software that adds support for geographic objects. 

### 1a) PostGIS setup tips for macOS
The following guides were of use to me:
* [How to install postgresql on a mac](https://launchschool.com/blog/how-to-install-postgresql-on-a-mac)
* [How to install postgis on mac os x](https://morphocode.com/how-to-install-postgis-on-mac-os-x/)
* [If you get errors when starting postgres on newer versions of macOS](https://stackoverflow.com/questions/25970132/pg-tblspc-missing-after-installation-of-latest-version-of-os-x-yosemite-or-el)


### 1b) Using postgress with pgAdmin

If you have used the above tutorials then following installation of postgres and creating your database you can 
login using pgadmin as `<your username>` at `127.0.0.1`. 

If you have trouble logging into your database this[stack overflow link](https://stackoverflow.com/questions/11919391/postgresql-error-fatal-role-username-does-not-exist)
may be of use.


My advice is to use pgAdmin 3 on macOS because it just works. 
If you want to use PgAdmin4 on macOS and encounter problems, the following may be of interest:

[Stack Overflow - Application server could not be contacted](https://stackoverflow.com/questions/43211296/pgadmin4-postgresql-application-server-could-not-be-contacted)
 
 Relevant commands:
1) `pg_ctl -D /usr/local/var/postgres stop -s -m fast`
2) `pg_ctl -D /usr/local/var/postgres start -s -m fast`
3) `pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log restart`


## 2) Get OSM data into PostGIS
Using OSM2pgSQL to create a PostGIS Database, on osx this can be installed using homebrew: 
`brew install osm2pgsql`
Use OSM2PGSQL to convert OSM data into a pgsql database:
http://learnosm.org/en/osm-data/osm2pgsql/


Command run with style file and osm data in working directory: 

`osm2pgsql -c -d osm -U mpm2017 -H localhost -S default.style nepal-latest.osm.pbf` 

If you get an error like 'ERROR:  type "geometry" does not exist' then make sure you have added the postGIS extension to the database that you are trying to add the features to

## 3) Setting up GDAL and Python
The library that handles the reading and writing of raster data is called[GDAL](http://www.gdal.org). 

### 3a) OSX Setup
There are many options for installing python and GDAL but on OSX I would recommend using the[homebrew](https://brew.sh) package manager.


## 4) Generating Rasters
Once you have the OSM data in a postGIS database it is time 


## 5) Building and Interpreting Maps in QGIS
A useful (and free) tool for working with the PostGIS database and raster imagery for this project is [QGIS](http://qgis.org).


### Creating a Buildings Layer 
To create the building 
### Adding Raster Layers

### Scales and Blending