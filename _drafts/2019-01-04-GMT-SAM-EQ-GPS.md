---
title: 'Plot USGS SAM topography, earthquake data, GPS vectors, NDVI and rainfall with GMT'
date: 2019-01-04
read_time: false
permalink: /posts/2019/01/GMT-SAM-EQ-GPS/
-- tags:
  - GMT
  - SAM
  - GPS
  - EQ
  - Earthquake
  - NDVI
  - Andes
---

South America is characterized by steep gradients in tectonism, topography, and climate. Here, we show how these gradients can be visualized with various maps showing topography, earthquakes, GPS vectors, NDVI vegetation cover, and TRMM rainfall distribution. It is also shown, how an E-W profile can be generated for these data. The data and scripts are available at [GMT-SAM-EQ-GPS-NDVI-PRECIP](https://github.com/BodoBookhagen/GMT-SAM-EQ-GPS-NDVI-PRECIP). 

# Data sources and setup
Topographic data are needed. In this example, we rely on the 15s global topography obtained from [ftp://topex.ucsd.edu/pub/srtm15_plus/](ftp://topex.ucsd.edu/pub/srtm15_plus/). The file [earth_relief_15s.nc](ftp://topex.ucsd.edu/pub/srtm15_plus/earth_relief_15s.nc) is needed. Use `wget ftp://topex.ucsd.edu/pub/srtm15_plus/earth_relief_15s.nc` to obtain the data. This will come in handy for many other examples as well and it will be good to keep a copy on your local computer. *NOTE: These data are 2.6GB*.

Alternatively, you can download the [SRTM DEM](https://www2.jpl.nasa.gov/srtm/) at 30m or 90m spatial resolution. I suggest to look at the most recent [NASADEM](https://earthdata.nasa.gov/community/community-data-system-programs/measures-projects/nasadem). Data have not been finalized yet (but will so soon) and can be accessed [here](https://e4ftl01.cr.usgs.gov/provisional/MEaSUREs/NASADEM/). There is a neat github repository [nasadem](https://github.com/dshean/nasadem) by David Shean that provides some scripts for downloading and preprocessing. [TanDEM-X](https://github.com/dshean/tandemx) data are also available. In any case, for our purposes the 15s data will be just fine.

## Conda setup
Install and start the GMT environment with:
```bash
conda create -y -n gmt5 gmt=5* python=3.6 scipy pandas numpy matplotlib scikit-image gdal spyder imagemagick
source activate gmt5
```

Depending on your system, you may need to change the order of the channels with the following and then re-run the `conda create` command from above:
```bash
conda config --remove channels defaults
conda config --append channels conda-forge/label/dev
```

Clone the repository with:
```bash
git clone https://github.com/BodoBookhagen/GMT-SAM-EQ-GPS-NDVI-PRECIP`.
```

## Prepare Data
### Prepare grid / raster data
#### Prepare DEM data
*NOTE: These data are not included on the github page, because they are too large to be stored on github*

We first need to prepare the DEM data for the region of interest. Define the region of interest:
```bash
REGION=-80/-60/-40/-15
```

Next, we clip this region from the global Topo15s file (see above). Make sure to properly set the path to the location of the earth_relief_15s.nc file. 
```bash
TOPO15_GRD_NC=/PATH/TO/FILE/earth_relief_15s.nc
TOPO15_GRD_NC_CentralAndes=earth_relief_15s_CentralAndes.nc
gmt grdcut -R$REGION $TOPO15_GRD_NC -G$TOPO15_GRD_NC_CentralAndes
```

You can turn this into a more fancy bash-style script that verifies if the file exist. This will ensure that you only create
```bash
TOPO15_GRD_NC=/PATH/TO/FILE/earth_relief_15s.nc
TOPO15_GRD_NC_CentralAndes=earth_relief_15s_CentralAndes.nc
if [ ! -e $TOPO15_GRD_NC_CentralAndes ]
then
    echo "generate Topo15S Clip $TOPO15_GRD_NC_CentralAndes"
    gmt grdcut -R$REGION $TOPO15_GRD_NC -G$TOPO15_GRD_NC_CentralAndes
fi
```

Next, generate a hillshade image. Here, we use more sophisticated hillshade calculation and store in `$TOPO15_GRD_HS_NC`:
```bash
TOPO15_GRD_NC=$TOPO15_GRD_NC_CentralAndes
TOPO15_GRD_HS_NC=earth_relief_15s_CentralAndes_HS.nc
if [ ! -e $TOPO15_GRD_HS_NC ]
then
    echo "generate hillshade $TOPO15_GRD_HS_NC"
    gmt grdgradient $TOPO15_GRD_NC -Ne0.6 -Es75/55+a -G$TOPO15_GRD_HS_NC
fi
```
If you instead want to have a simpler hillshading with less relief, use something akin to the Peucker algorithm. We call this `$TOPO15_GRD_HS2_NC`.
```bash
TOPO15_GRD_HS2_NC=earth_relief_15s_CentralAndes_HS_peucker.nc
if [ ! -e $TOPO15_GRD_HS2_NC ]
then
    echo "generate hillshade $TOPO15_GRD_HS2_NC"
    gmt grdgradient $TOPO15_GRD_NC -Nt1 -Ep -G$TOPO15_GRD_HS2_NC
fi
```

#### Prepare MODIS EVI and NDVI raster data
These have been created from the MODIS product [MOD13A3]() and compiled to annual and monthly averages. Data-preprocessing is not shown here. We have generated a Geotiff file containing mean NDVI and EVI from 2001-2017 stored in the files MOD13A3_2001-2017NDVImn.tif and MOD13A3_2001-2017EVImn.tif.

We use `gmt grdcut` to extract the relevant region.
```bash
MOD13A3_NDVI=/raid-everest/data/MODIS/MOD13A3/MOD13A3_2001-2017NDVImn.tif
MOD13A3_NDVI_CentralAndes=MOD13A3_2001-2017NDVImn_CentralAndes.nc
if [ ! -e $MOD13A3_NDVI_CentralAndes ]
then
    echo "generate NDVI Mean Clip $MOD13A3_NDVI_CentralAndes"
    gmt grdcut -R$REGION $MOD13A3_NDVI -G$MOD13A3_NDVI_CentralAndes
fi
```

Next, we resample this file to the resolution of the topographic data to allow hillshading and more sophisticated visualization. Resampling will be forced with number of lines and rows that have been obtained with `gdalinfo earth_relief_15s_CentralAndes.nc`: 4801x6001.
```bash
MOD13A3_NDVI_CentralAndes_rTOPO15=MOD13A3_2001-2017NDVImn_CentralAndes_Topo15S.nc
if [ ! -e $MOD13A3_NDVI_CentralAndes_rTOPO15 ]
then
    echo "resample NDVI Mean Clip $MOD13A3_NDVI_CentralAndes_rTOPO15"
    gmt grdsample $MOD13A3_NDVI_CentralAndes -R$REGION -I4801+/6001+ -G$MOD13A3_NDVI_CentralAndes_rTOPO15
fi
```
We do the same for the EVI data:
```bash
MOD13A3_EVI=/raid-everest/data/MODIS/MOD13A3/MOD13A3_2001-2017EVImn.tif
MOD13A3_EVI_CentralAndes=MOD13A3_2001-2017EVImn_CentralAndes.nc
MOD13A3_EVI_CentralAndes_rTOPO15=MOD13A3_2001-2017EVImn_CentralAndes_Topo15S.nc
if [ ! -e $MOD13A3_EVI_CentralAndes ]
then
    echo "generate EVI Mean Clip $MOD13A3_EVI_CentralAndes"
    gmt grdcut -R$REGION $MOD13A3_EVI -G$MOD13A3_EVI_CentralAndes
fi

if [ ! -e $MOD13A3_EVI_CentralAndes_rTOPO15 ]
then
    echo "resample EVI Mean Clip $MOD13A3_EVI_CentralAndes_rTOPO15"
    gmt grdsample $MOD13A3_EVI_CentralAndes -R$REGION -I4801+/6001+ -G$MOD13A3_EVI_CentralAndes_rTOPO15
fi
```

## Prepare vector data / shapefiles
We have used various software to generate polygon files outlining the hydrologic basins of South America. An easy way to start is to look at [Hydroshed](https://hydrosheds.cr.usgs.gov/index.php). Here, we provide several shapefiles in the subdirectory [GMT_vector_data](GMT_vector_data). The shapefiles have been converted to GMT files using `ogr2ogr` and the projection has been changed from UTM-19S to GEOGRAPHIC projection (EPSG 4326, where necessary). In the subdirectory GMT_vector_data, run:
```bash
ogr2ogr -f GMT puna_1bas_GEOGRAPHIC_WGS84.gmt puna_1bas_GEOGRAPHIC_WGS84.shp
ogr2ogr -f GMT -t_srs epsg:4326 AltiplanoPuna_1basin_UTM19S_WGS84.gmt AltiplanoPuna_1basin_UTM19S_WGS84.shp
ogr2ogr -f GMT -t_srs epsg:4326 SA_basins_15s_puna_UTM19S_WGS84.gmt SA_basins_15s_puna_UTM19S_WGS84.shp
```
Now, these gmt files can be plotted with `psxy`.

### Prepare OSM vector data
The [OpenStreetMap (OSM)](https://www.openstreetmap.org/) dataset is very useful for showing high-resolution shorelines, anthropogenic infrastructure and a variety of other data that are not contained in the GMT vector files. OSM data come in a different format and will need to be converted before usage. [OSM Wiki](https://wiki.openstreetmap.org/wiki/Downloading_data) provides some insights, but there are additional steps necessary. this is a multi-step process.

First, get the data from [geofabrik](https://www.geofabrik.de/). They provide pbf files for every continent (or country) that can be converted into GMT or shapefile format:
```bash
wget https://download.geofabrik.de/south-america-latest.osm.pbf
```

Next, the OSM-pbf file needs to be converted to GMT files. This will need to be done for every attribute separately to keep your database nice and clean. We usually use the following. 
*NOTE: gdal/ogr will need to have been compiled with GEOS, SQL and pbf support!*

*NOTE: In order to generate the railway database, you have to change /usr/share/gdal/2.2/osmconf.ini and allow the tag railway to be created. See [here](https://wiki.openstreetmap.org/wiki/User:Bgirardot/How_To_Convert_osm_.pbf_files_to_Esri_Shapefiles). You first need to identify the relevant osmconf.ini file using `locate osmconf.ini` and then edit that to include additional attributes and fields.*

*NOTE: In order to generate the volcano database, you have to change /usr/share/gdal/2.2/osmconf.ini and allow the tag natural to be created.*

```bash
ogr2ogr -f "GMT" south-america_roads01.gmt south-america-latest.osm.pbf -progress -sql "select highway from lines where highway in ('primary', 'secondary', 'tertiary', 'unclassified', 'residential')" 
ogr2ogr -f "GMT" south-america_roads02.gmt south-america-latest.osm.pbf -progress -sql "select highway from lines where highway not in ('primary', 'secondary', 'tertiary', 'unclassified', 'residential')" 
ogr2ogr -f "GMT" south-america_lakes.gmt south-america-latest.osm.pbf -progress -sql "select natural from multipolygons where natural in ('water')" 
ogr2ogr -f "GMT" south-america_wetlands.gmt south-america-latest.osm.pbf -progress -sql "select natural from multipolygons where natural in ('wetland')" 
ogr2ogr -f "GMT" south-america_rivers.gmt south-america-latest.osm.pbf -progress -sql "select waterway from lines where waterway in ('river')" 
ogr2ogr -f "GMT" south-america_railway.gmt south-america-latest.osm.pbf -progress -sql "select railway from lines where railway in ('rail')" 
ogr2ogr -f "GMT" south-america_volcano.gmt south-america-latest.osm.pbf -progress -sql "select natural from points where natural in ('volcano')" 
```
If you replace `-f "GMT"` with `-f "ESRI Shapefile"`, you create ESRI shapefiles as output.

These are large files and processing them with GMT for map making will take some time. I suggest to clip this to the area of interest (will make map making a little faster). Here, we use the coordinates from the `$REGION` variable (see above). `-clipsrs` expects xmin ymin xmax ymax coordinates.

```bash
ogr2ogr -f "GMT" CentralAndesroads01.gmt south-america_roads01.gmt -clipsrc -80 -40 -60 -15
ogr2ogr -f "GMT" CentralAndesroads02.gmt south-america_roads02.gmt -clipsrc -80 -40 -60 -15
ogr2ogr -f "GMT" CentralAndeslakes.gmt south-america_lakes.gmt -clipsrc -80 -40 -60 -15
ogr2ogr -f "GMT" CentralAndeswetlands.gmt south-america_wetlands.gmt -clipsrc -80 -40 -60 -15
ogr2ogr -f "GMT" CentralAndesrivers.gmt south-america_rivers.gmt -clipsrc -80 -40 -60 -15
ogr2ogr -f "GMT" CentralAndesrailway.gmt south-america_railway.gmt -clipsrc -80 -40 -60 -15
ogr2ogr -f "GMT" CentralAndesvolcano.gmt south-america_volcano.gmt -clipsrc -80 -40 -60 -15
```

The files `CentralAndeslakes.gmt` can be plotted with `gmt psxy`.

### Prepare city dataset from OSM
First, edit osmconf.ini and add `city` to the list of attributes in the section `[points]`.
The line `attributes` in the `[points]` section should read:
```bash
attributes=name,barrier,highway,ref,address,is_in,place,man_made,city,population
```

Next, extract the cities with `ogr2ogr` and store name and population `select city,name,population` and select only cities with a stored name `where name is not null`:
```bash
ogr2ogr -f "GMT" south-america_cities_with_names.gmt south-america-latest.osm.pbf -progress -sql "select city,name,population from points where name is not null" 
```

We create a second dataset containing only cities with a stored population:
```bash
ogr2ogr -f "GMT" south-america_cities_with_population.gmt south-america-latest.osm.pbf -progress -sql "select city,name,population from points where population is not null" 
```

Alternatively, create a dataset containing any city (also without names):
```bash
ogr2ogr -f "GMT" south-america_cities.gmt south-america-latest.osm.pbf -progress -sql "select city,name,population from points" 
```

### Prepare simplified city dataset
City locations are also included in the OSM dataset, but a simpler CSV file will do it as well. There are many datasets available, here we are using a free city CSV version currently hosted at [maxmind](https://www.maxmind.com/en/free-world-cities-database). The CSV contains:
`Country,City,AccentCity,Region,Population,Latitude,Longitude`.
The file contains a global database of cities - we are only interested in showing a few for South America and we preprocess the data to select only Santiago de Chile, Salta, Mendoza and La Paz.
*NOTE: We have converted the gzip-compressed file to a bzip2 compressed file*

First we search for the country ar (Argentina) and city Salta and we only use the longitude, latitude columns. In the second command, we add the label Salta to the end of the first row:

```bash
bzip2 -dc worldcitiespop.txt.bz2 | grep -w ar | grep -w Salta | gmt select -i6,5 >salta.txt
sed -i "1 s|$| Salta|" salta.txt
```
This can be done similarily for the other cities:
```bash
bzip2 -dc worldcitiespop.txt.bz2 | grep -w ar | grep ",Mendoza" | gmt select -i6,5 >mendoza.txt
sed -i "1 s|$| Mendoza|" mendoza.txt

bzip2 -dc worldcitiespop.txt.bz2 | grep -w bo | grep ",La Paz,04" | gmt select -i8,7 >lapaz.txt
sed -i "1 s|$| LaPaz|" lapaz.txt

bzip2 -dc worldcitiespop.txt.bz2 | grep -w cl | grep ",Santiago" | gmt select -i6,5 >SdC.txt
sed -i "1 s|$| SdC|" SdC.txt
```
The txt files can be plotted with `gmt psxy`.


### Prepare Earthquake catalog from USGS
There exists different EQ catalogs. Here, we download data from the [USGS](https://earthquake.usgs.gov/earthquakes/search/) by selecting a range of magnitude, time, and geographic region and write to a CSV file. If you use the entire geographic region of SAM (or the region we have been working with), you will need to select the magnitude in steps, to produce less than 20k searches (max. allowed number of records to export). Because we will plot the magnitudes with different sizes/colors, this will be useful in any case. We have generated several files with the following names (should be self explanatory): USGS_EQ_CentralAndes_1970_2018_mag3.5_to_4.csv, USGS_EQ_CentralAndes_1970_2018_mag4_to_4.5.csv, USGS_EQ_CentralAndes_1970_2018_mag4.5_to_5.csv, USGS_EQ_CentralAndes_1970_2018_mag5_to_5.5.csv, USGS_EQ_CentralAndes_1970_2018_mag5.5_to_6.csv, USGS_EQ_CentralAndes_1970_2018_mag6_to_9.csv. 
We compress them with `bzip2`. `bzip2` is much more efficient in compressing ASCII text files than `gzip`. A quick test shows that file USGS_EQ_CentralAndes_1970_2018_mag3.5_to_4.csv compressed to 291293 bytes (291 kb) with `bzip2` and to 410052 bytes (410 kb) with `gzip` (using best compression option `-9` for both algorithms). We combine magnitude ranges 4 to 5 and 5 to 6:

```bash
bzip2 -9 USGS_EQ_CentralAndes_1970_2018_mag3.5_to_4.csv

cp USGS_EQ_CentralAndes_1970_2018_mag4_to_4.5.csv USGS_EQ_CentralAndes_1970_2018_mag4_to_5.csv
cat USGS_EQ_CentralAndes_1970_2018_mag4.5_to_5.csv >> USGS_EQ_CentralAndes_1970_2018_mag4_to_5.csv
bzip2 -9 USGS_EQ_CentralAndes_1970_2018_mag4_to_5.csv

cp USGS_EQ_CentralAndes_1970_2018_mag5_to_5.5.csv USGS_EQ_CentralAndes_1970_2018_mag5_to_6.csv
cat USGS_EQ_CentralAndes_1970_2018_mag5.5_to_6.csv >>USGS_EQ_CentralAndes_1970_2018_mag5_to_6.csv
bzip2 -9 USGS_EQ_CentralAndes_1970_2018_mag5_to_6.csv

bzip2 -9 USGS_EQ_CentralAndes_1970_2018_mag6_to_9.csv
```

These files are available in the [GMT_vector_data](GMT_vector_data) directory.

## Prepare GPS vector data
