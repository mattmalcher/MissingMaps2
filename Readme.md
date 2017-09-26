#Where the Maps are Missing 2

## Intro
The point of this document is to describe what the tools in this repository are, 
why they are built the way they are and how to use them.

### What are these tools?
These tools take spatial world population data in raster form from [worldpop](http://www.worldpop.org.uk) and locations of building vector data from [open street map](https://www.openstreetmap.org) and compare the two.
The idea is that this provides an indication of where there are people but no maps or 'where the maps are missing'.

The tools in this repository are a development of work done by Simon B. Johnson at the British Red Cross. Please see his 
[Medium post](https://medium.com/@Simon_B_Johnson/where-are-the-maps-missing-b22ceedb26f3#.l8rzisyu1)
and
[GitHub repository](https://github.com/SimonbJohnson/missingmaps_whatsmissing)
for context and a nice write-up of the original project.

#### Functional Overview:
Inputs:
* Worldpop Data (geotiff raster of population density)
* Open Street Map data for a region (contains existing map data including building locations.)

Processing:
* Store OSM data in PostGIS database
* Query PostGIS database and count the number of buildings in areas equivalent to pixels in the worldpop raster
* Compare OSM building count to worldpop people count

Outputs:
* Raster showing OSM building density
* Comparison data (geotiff raster) showing discrepancies between number of buildings and popuation density. 
*i.e. an indication of where mapping data is missing*

### Why have they been made?

Many of the places where disasters occur are 'missing' from the map.
[Missing Maps](http://www.missingmaps.org) is a project to give first responders the information they need to assist 
 people effectively. 
 
The originator, Simon has many other responsibilities (check out his [blog](https://medium.com/@Simon_B_Johnson)). As such, updating the tools used for the original blog post has 
fallen somewhere down his list of priorities, off the bottom, then into this repository.

### What is Next?
As per Simon's original post there are several areas for improvement.
* Investigate more than just buildings
* Creating more intelligent feedback on when to trust World Pop data in well mapped areas
* Create aggregated/fuzzy views to account for World Pop noise and allow easier exploring
* Create maps for all possible countries

Further to these goals it is also important to make the tool more accessible so that it can be leveraged to inform future
mapping efforts. This could take the form of an interactive, web hosted map.

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
[PostGIS](http://www.postgis.org) is an extension for the [PostgreSQL](https://www.postgresql.org) relational database 
software that adds support for geographic objects. It is useful because it allows us to store and manipulate large 
amounts of geospatial data in an efficient way.

### 1a) PostGIS setup tips for macOS
The following guides were of use to me:
* [How to install postgresql on a mac](https://launchschool.com/blog/how-to-install-postgresql-on-a-mac)
* [How to install postgis on mac os x](https://morphocode.com/how-to-install-postgis-on-mac-os-x/)
* [If you get errors when starting postgres on newer versions of macOS](https://stackoverflow.com/questions/25970132/pg-tblspc-missing-after-installation-of-latest-version-of-os-x-yosemite-or-el)

### 1b) PostGIS setup tips for Windows
A good guide on getting PostGIS running on Windows can be found at: 
[learnosm.org](http://learnosm.org/en/osm-data/postgresql/) 

### 1c) Using postgress with pgAdmin
pgAdmin is a tool for administrating PostgreSQL databases. It is not strictly neccesary but you may find it useful for debugging things as it provides a
relatively easy way to interrogate and view the layout of the PostGIS database.

If you have used the macOS tutorials then following installation of postgres and creating your database you can 
login using pgadmin as:

 `<your username>` @ `127.0.0.1`. 

If you have trouble logging into your database 
this [stack overflow link](https://stackoverflow.com/questions/11919391/postgresql-error-fatal-role-username-does-not-exist) may be of use.

My advice is to use pgAdmin 3 on macOS because it just works. 
If you use PgAdmin4 and encounter problems, the following may be of interest:

[Stack Overflow - Application server could not be contacted](https://stackoverflow.com/questions/43211296/pgadmin4-postgresql-application-server-could-not-be-contacted)
 
 Relevant commands for starting/stopping and restarting the server:
1) `pg_ctl -D /usr/local/var/postgres stop -s -m fast`
2) `pg_ctl -D /usr/local/var/postgres start -s -m fast`
3) `pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log restart`


## 2) Get OSM data into PostGIS
The intent of the tools in this repository is to work with relatively large amounts of OSM data. In particular we are 
interested in buildings and their locations. 

Buildings are stored in OSM as [multipolygons](http://wiki.openstreetmap.org/wiki/Relation:multipolygon). 
For a country sized area there can be millions of multipolygons. This is why we are using PostGIS as our datastore 
rather than working with formats such as geojson.

OSM data for countries can be found readily on the internet. (See the 
OSM [wiki](http://wiki.openstreetmap.org/wiki/Downloading_data) for an overview.)
For this project the country extracts found at [geofabrik](https://download.geofabrik.de) make an ideal source for building data.
These extracts come in multiple formats, for this project we will use the [`.osm.pbf`](http://wiki.openstreetmap.org/wiki/PBF_Format) format data.

You can use the OSM2pgSQL command line tool to create a PostGIS database from the `.osm.pbf` file.

A good guide for installing and using osm2pgsql on windows can be found 
at [learnosm.org](http://learnosm.org/en/osm-data/osm2pgsql/). 
On macOS osm2pgsql can be installed using homebrew: `brew install osm2pgsql`

To run the tool you will need to have a [style file](https://wiki.openstreetmap.org/wiki/Osm2pgsql#Import_style) which 
defines which bits of the OSM file get stored in the database and how they are stored.


Once you have osm2pgsql installed, and have downloaded a style file and some osm data ready to go you can run the following:

`osm2pgsql -c -d <postgress database name> -U <postgress username> -H localhost -S default.style <download from geofabrik>.osm.pbf` 

This should take half an hour or so for a country sized region (perhaps less if you are on an SSD). If you get an error like 'ERROR:  type "geometry" does not exist' then make sure you have added the postGIS extension to the database that you are trying to add the features to

## 3) Setting up GDAL

_It is assumed that you already have python 3 installed. If you don't, do so at this point in the guide._

The library that handles the reading and writing of raster data is called [GDAL](http://www.gdal.org). We will be 
interfacing with GDAL using python and as such need the associated bindings installed.

### 3a) macOS Setup
There are many options for installing python and GDAL but on OSX I would recommend using 
the [homebrew](https://brew.sh) package manager. This will install the python bindings as well as GDAL itself.

There is also a graphical setup for GDAL on macOS which can be found at [kyngchaos.com](http://www.kyngchaos.com/software/frameworks).
(Unsure if this sets up bindings for you)

### 3a) Windows Setup

You probably want to take a look at [osgeo.org](https://trac.osgeo.org/osgeo4w/wiki) to get GDAL and its python bindings 
set up.

## 4) Generating Rasters
From Step 2 you have OSM data in a postGIS database. Now it is time to manipulate this and compare it to the population 
rasters obtained from worldpop.

You will want to download some worldpop raster data from their [get data](http://www.worldpop.org.uk/data/data_sources/) page.
This project has been using individual country data. On the summary page for each country there is a 
'Download Individual Datasets' link at the bottom of the page. Please read the dataset details in the right hand side
to understand what the raster in the file you are downloading is.

### 4a) Directory Stucture

There are several .py files in the base folder of the repository these are:
* Functions.py - Contains functions used by the other two files.
* genOSMraster.py - Generates a raster showing OSM building density.
* genDIFFraster.py - Reads in population and building density rasters and compares them.

In addition to this there are several directories:
* Input - Storage location for worldpop .tif files and OSM *.osm.pbf's
* Output - Directory which rasters are written to.
* QGIS - Contains maps based on the processed data.
* Reference - Miscellaneous files for reference, not used.

You will need to edit the `pop_tiff_name` variable in the `genOSMraster` and `genDIFFraster` scripts to point to the 
relevant worldpop geotiff.

There is a .gitignore file set up to ignore raster and osm data to avoid keeping massive non-text files in git.

### 4b) Generate an OSM building count raster

Once you have your worldpop tiff in place and a populated postGIS database you can run `genOSMraster` to generate a 
geotiff at: `./Output/osm_count.tiff`. 

This geotiff will match the format of the worldpop geotiff provided as an input 
and the value of the raster in each pixel is the count of the buildings in OSM in the equivalent area. 
The count of buildings is considered as multipolygons where the building tag is not null - 
(i.e. any multipolygon with a building tag.)

_Running this script for Nepal with approx 3 million buildings takes <10 mins on a 2008 era laptop._

### 4c) Generate difference rasters

Following the generation of `osm_count.tiff` you can then compare it to the worldpop raster. 
The script `genDIFFraster.py` is set up to do this. It uses the functions in `Functions.py` to read in and write out 
raster data to geotiff files. The comparisons are done using numpy arrays and the associated tools to avoid needing to 
loop over items in the raster.

A masked array are used for the worldpop raster when it is read in. This handles the areas in the raster which have 
missing values, to which GDAL assigns large negative values. This can vary from raster to raster, in some cases a value 
such as '-3e42' has been observed, which if not masked can create issues with further processing.

Where there are no buildings in OSM the OSM raster has a value of 0, this creates numerical problems when calculating 
say people/buildings or people per building. Therefore where the osm raster is 0 it is set to a value of 0.01. This value 
is from Simon's [blog post](https://medium.com/@Simon_B_Johnson/where-are-the-maps-missing-b22ceedb26f3#.l8rzisyu1) which
investigated different values.

The raster operations and output tiff's generated by default may not be what you want! Understand and think about what you are 
putting in and what you expect to get out. It should be easy to follow the example in `genDIFFraster.py` to create and 
output different comparison rasters using numpy array operations.

## 5) Building Maps in QGIS
A useful (and free) tool for working with the PostGIS database and raster imagery for this project is [QGIS](http://qgis.org).

Once you have a PostGIS database of an area as well as some rasters you can begin to plot them on maps and create something useful!

### 5a) Creating a Buildings Layer 
To create the buildings layer you can connect QGIS to your postGIS database which contains the OSM data for the area, 
and filter what is displayed:

Layer > Add Layer > Add PostGIS layers

You will then get a dialogue box for 'adding PostGIS Table(s)', press the button to create a new connection, then input the
 name, username and password for your PostGIS database created in step 2.
 
Once you have defined your connection you should be able to connect to it and see the database tables listed in 
the 'adding PostGIS Table(s)' dialogue. Add the polygon layer to your QGIS Map. 

The polygon layer will contain all polygons (regional areas, swimming pools, parks etc) - not just buildings, so to 
filter it go to to:

Layer > Filter

This will bring up a dialogue allowing you to build complex criteria to filter the layer by.
We want only polygons where a building tag exists so in the 'Provider specific filter expression' box enter:

`"building" is not null`

This will remove all the polygons which do not have a building tag.

### 5b) Adding Raster Layers

Adding the raster layers is simple; drag and drop the relevant .tif into the layers panel in QGIS.
This will add the layer and display it as a 'singleband grey' layer.

To modify the display of the layer go to:

Layer > Properties

You may find it more pleasing to display the layer as 'singleband pseudocolour'. Ensure the max and min are set to values 
which match your understanding and expectations for the data then press the classify button under the value/colour/label box
to automatically add scale items within the min max range.

If you want to overlay this layer on a base map or similar, investigate the 'blending mode' options in the colour rendering box.
(Tip: white renders as transparent when the blending mode is multiply.)

For finer control you can double click on items in the value/colour/label box and edit the display properties one 
band at a time.

### 5c) Adding Base Layers
You may find it useful to display a base layer such as aerial imagery or the OSM basemap. To do this easily you can use 
the Open Layers Plugin. Install this plugin from:

Plugins > Manage and Install Plugins

Once installed you can then add layers from:

Web > OpenLayers Plugin.

