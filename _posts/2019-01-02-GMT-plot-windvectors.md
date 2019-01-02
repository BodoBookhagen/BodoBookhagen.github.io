---
title: 'Plot ECMWF wind vectors with GMT'
date: 2019-01-02
permalink: /posts/2019/01/GMT-plot-windvectors/
-- tags:
  - GMT
  - wind
  - vector
  - grdvector
  - ECMWF
---

Visualizing wind fields with GMT can be tricky, especially if the NETCDF data will need to be pre-processed. Here is a short description of some steps necessary to create visually appealing maps from ECMWF u and v wind fields using GMT. The example shown is for South America. The data and scripts are available at [GMT-plot-windvectors-SAM](https://github.com/BodoBookhagen/GMT-plot-windvectors-SAM). 

# Data sources and setup
The data used in this example are [ECMWF-EI-WND_1999_2013_DJF_200_SAM.nc](ECMWF-EI-WND_1999_2013_DJF_200_SAM.nc) for the 200hPA mean DJF wind from 1999 to 2013 for the South American domain. These have been generated and preprocessed with [CDO](https://code.mpimet.mpg.de/projects/cdo/).

In addition, you will need topographic data for hillshading purposes. In this example, I am using a 15s global topography obtained from [ftp://topex.ucsd.edu/pub/srtm15_plus/](ftp://topex.ucsd.edu/pub/srtm15_plus/). The file [earth_relief_15s.nc](ftp://topex.ucsd.edu/pub/srtm15_plus/earth_relief_15s.nc) is needed. This will come in handy for many other examples as well and it will be good to keep a copy on your local computer. 

Install and start the GMT environment with:
```bash
conda create -y -n gmt5 gmt=5* python=3.6 scipy pandas numpy matplotlib scikit-image gdal spyder imagemagick
source activate gmt5
```

Clone the repository with:
```bash
git clone https://github.com/BodoBookhagen/GMT-plot-windvectors-SAM.git`.
```

## Prepare Data
## Prepare DEM data
*NOTE: These data are not included on the github page, because they are too large to be stored on github*

We first need to prepare the DEM data for the region of interest. Define the region of interest:
```bash
REGION=-85/-30/-40/15
```

Next, we clip this region from the global Topo15s file (see above). Make sure to properly set the path to the location of the earth_relief_15s.nc file. 
```bash
TOPO15_GRD_NC=/PATH/TO/FILE/earth_relief_15s.nc
TOPO15_GRD_NC_CentralAndesAmazon=earth_relief_15s_CentralAndesAmazon.nc
gmt grdcut -R$REGION $TOPO15_GRD_NC -G$TOPO15_GRD_NC_CentralAndesAmazon
```

You can turn this into a more fancy bash-style script that verifies if the file exist. This will ensure that you only create
```bash
TOPO15_GRD_NC=/PATH/TO/FILE/earth_relief_15s.nc
TOPO15_GRD_NC_CentralAndesAmazon=earth_relief_15s_CentralAndesAmazon.nc
if [ ! -e $TOPO15_GRD_NC_CentralAndesAmazon ]
then
    echo "generate Topo15S Clip $TOPO15_GRD_NC_CentralAndesAmazon"
    gmt grdcut -R$REGION $TOPO15_GRD_NC -G$TOPO15_GRD_NC_CentralAndesAmazon
fi
```

Next, generate a hillshade image. Here, we use more sophisticated hillshade calculation and store in `$TOPO15_GRD_HS_NC`:
```bash
TOPO15_GRD_NC=$TOPO15_GRD_NC_CentralAndesAmazon
TOPO15_GRD_HS_NC=earth_relief_15s_CentralAndesAmazon_HS.nc
if [ ! -e $TOPO15_GRD_HS_NC ]
then
    echo "generate hillshade $TOPO15_GRD_HS_NC"
    gmt grdgradient $TOPO15_GRD_NC -Ne0.6 -Es75/55+a -G$TOPO15_GRD_HS_NC
fi
```
If you instead want to have a simpler hillshading with less relief, use something akin to the Peucker algorithm. We call this `$TOPO15_GRD_HS2_NC`.
```bash
TOPO15_GRD_HS2_NC=earth_relief_15s_CentralAndesAmazon_HS_peucker.nc
if [ ! -e $TOPO15_GRD_HS2_NC ]
then
    echo "generate hillshade $TOPO15_GRD_HS2_NC"
    gmt grdgradient $TOPO15_GRD_NC -Nt1 -Ep -G$TOPO15_GRD_HS2_NC
fi
```

## Prepare NETCDF wind file
The file `ECMWF-EI-WND_1999_2013_DJF_200_SAM.nc` is a typical output generated with CDO. It contains the mean u and v wind components for the DJF season from 1999 to 2013 for South America. If you want to obtain information about the NETCDF .nc file, use `ncdump`
```bash
ncdump -h ncdump -h ECMWF-EI-WND_1999_2013_DJF_200_SAM.nc
```

with output:
```bash
netcdf ECMWF-EI-WND_1999_2013_DJF_200_SAM {
dimensions:
	longitude = 111 ;
	latitude = 111 ;
	level = 1 ;
	time = UNLIMITED ; // (1 currently)
variables:
	float longitude(longitude) ;
		longitude:standard_name = "longitude" ;
		longitude:long_name = "longitude" ;
		longitude:units = "degrees_east" ;
		longitude:axis = "X" ;
	float latitude(latitude) ;
		latitude:standard_name = "latitude" ;
		latitude:long_name = "latitude" ;
		latitude:units = "degrees_north" ;
		latitude:axis = "Y" ;
	double level(level) ;
		level:standard_name = "air_pressure" ;
		level:long_name = "pressure_level" ;
		level:units = "millibars" ;
		level:positive = "down" ;
		level:axis = "Z" ;
	double time(time) ;
		time:standard_name = "time" ;
		time:units = "hours since 1900-01-01 00:00:00" ;
		time:calendar = "standard" ;
	float u(time, level, latitude, longitude) ;
		u:standard_name = "eastward_wind" ;
		u:long_name = "U component of wind" ;
		u:units = "m s**-1" ;
		u:_FillValue = -32767.f ;
		u:missing_value = -32767.f ;
	float v(time, level, latitude, longitude) ;
		v:standard_name = "northward_wind" ;
		v:long_name = "V component of wind" ;
		v:units = "m s**-1" ;
		v:_FillValue = -32767.f ;
		v:missing_value = -32767.f ;

// global attributes:
		:CDI = "Climate Data Interface version 1.6.4 (http://code.zmaw.de/projects/cdi)" ;
		:Conventions = "CF-1.0" ;
		:history = "Tue Dec 04 18:59:09 2018: cdo timmean ECMWF-EI-WND_1999_2013_DJF_200_domain.nc ECMWF-EI-WND_1999_2013_DJF_200_domain_timm.nc\n",
			"Thu Nov 29 17:25:03 2018: cdo sellonlatbox,-85,-30,-40,15 ECMWF-EI-WND_1999_2013_DJF_200.nc ECMWF-EI-WND_1999_2013_DJF_200_domain.nc\n",
			"Thu Nov 29 17:23:25 2018: cdo sellevel,200 ECMWF-EI-WND_1999_2013_DJF.nc ECMWF-EI-WND_1999_2013_DJF_200.nc\n",
			"Thu Nov 29 17:21:51 2018: cdo -b F32 -mergetime ECMWF-EI-WND_1999_DJF.nc ECMWF-EI-WND_2000_DJF.nc ECMWF-EI-WND_2001_DJF.nc ECMWF-EI-WND_2002_DJF.nc ECMWF-EI-WND_2003_DJF.nc ECMWF-EI-WND_2004_DJF.nc ECMWF-EI-WND_2005_DJF.nc ECMWF-EI-WND_2006_DJF.nc ECMWF-EI-WND_2007_DJF.nc ECMWF-EI-WND_2008_DJF.nc ECMWF-EI-WND_2009_DJF.nc ECMWF-EI-WND_2010_DJF.nc ECMWF-EI-WND_2011_DJF.nc ECMWF-EI-WND_2012_DJF.nc ECMWF-EI-WND_2013_DJF.nc ECMWF-EI-WND_1999_2013_DJF.nc\n",
			"Sun Sep 18 19:58:20 2016: cdo -b F32 mergetime ECMWF-EI-WND_2012_12.nc ECMWF-EI-WND_2013_01.nc ECMWF-EI-WND_2013_02.nc ECMWF-EI-WND_2013_DJF.nc\n",
			"Sun Sep 18 19:18:03 2016: cdo selmon,02 ECMWF-EI-WND_2013_mon.nc ECMWF-EI-WND_2013_02.nc\n",
			"Sun Sep 18 19:10:44 2016: cdo merge ECMWF-EI-XWND_2013_mon.nc ECMWF-EI-YWND_2013_mon.nc ECMWF-EI-WND_2013_mon.nc\n",
			"Tue Sep 13 13:34:07 2016: cdo -b F32 -monmean -cat ECMWF-EI-YWND-A+2013*.nc ECMWF-EI-YWND_2013_mon.nc\n",
			"2015-11-22 13:06:42 GMT by grib_to_netcdf-1.12.3: grib_to_netcdf ECMWF-EI-YWND-A+2013_01_01_00.grb -o ECMWF-EI-YWND-A+2013_01_01_00.nc" ;
		:CDO = "Climate Data Operators version 1.6.4 (http://code.zmaw.de/projects/cdo)" ;
}
```

Alternatively, and if you have a working CDO setup, use the following to obtain the variables contained in the NETCDF file.
```bash
cdo -s showname ECMWF-EI-WND_1999_2013_DJF_200_SAM.nc
```

Let's turn the NETCDF int a useful format to work with. First, define a variable with the filename:
```bash
ECMWF_WND="ECMWF-EI-WND_1999_2013_DJF_200_SAM.nc"
```
The file contains both, the u and v wind direction, and it is easier to work with if you pull these out. We do this with `grdconvert`. With `?` you can access the variables in the NETCDF file (see above for names). First we work with the u component:

```bash
gmt grdconvert ${ECMWF_WND}?u -G${ECMWF_WND::-3}_u.nc
```

CDO likes to store files with longitudes from 0 to 360. I prefer -180 to +180 and will apply this in the following step. *NOTE: This is not necessary, but most other data have longitude values between -180 and 180 and I like to keep it consistent. This also makes clipping and cutting easier*:
```bash
gmt grdedit ${ECMWF_WND::-3}_u.nc -R-85/-30/-40/15
```
Because the convention for meteorologic data are reversed compared to map data, we have to flip the sign of the u component.

```bash
gmt grdmath ${ECMWF_WND::-3}_u.nc NEG = ${ECMWF_WND::-3}_u.nc
```

Next, we do the same for the v component:
```bash
gmt grdconvert ${ECMWF_WND}?v -G${ECMWF_WND::-3}_v.nc
gmt grdedit ${ECMWF_WND::-3}_v.nc -R-85/-30/-40/15
gmt grdmath ${ECMWF_WND::-3}_v.nc NEG = ${ECMWF_WND::-3}_v.nc
```

The u and v components can now be turned into a magnitude or wind velocity grid. We use the equation sqrt(u^2+v^2). We also set the proper variable name and unit with `grdedit`:
```bash
gmt grdmath ${ECMWF_WND::-3}_v.nc 2 POW ${ECMWF_WND::-3}_u.nc 2 POW ADD SQRT = ${ECMWF_WND::-3}_magnitude.nc
gmt grdedit ${ECMWF_WND::-3}_magnitude.nc -D+z"Wind Magnitude"+r"sqrt(u^2 plus v^2)"
```

If you verify the output file with
```bash
gmt grdinfo ${ECMWF_WND::-3}_magnitude.nc
```
You will see that the units are properly set:
```bash
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: Title: Produced by grdmath
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: Command: grdmath ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_v.nc 2 POW ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_u.nc 2 POW ADD SQRT = ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: Remark: sqrt(u^2 plus v^2)
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: Gridline node registration used [Geographic grid]
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: Grid file format: nf = GMT netCDF format (32-bit float), COARDS, CF-1.5
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: x_min: -85 x_max: -30 x_inc: 0.5 name: longitude [degrees_east] n_columns: 111
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: y_min: -40 y_max: 15 y_inc: 0.5 name: latitude [degrees_north] n_rows: 111
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: z_min: 0.0781670808792 z_max: 30.9823875427 name: Wind Magnitude [m s**-1]
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: scale_factor: 1 add_offset: 0
ECMWF-EI-WND_1999_2013_DJF_200_domain_timm_magnitude.nc: format: classic
```
This also tells you that we have values between ~0 and ~30 m/s (see range of `z_min` and `z_max`).

Last, you want to make sure that you can overlay the grids with the topography. Here, I resample the magnitude grid to the topographic grid:
```bash
if [ ! -e ${ECMWF_WND::-3}_magnitude_topo15.nc ]
then
    echo "resample to ${ECMWF_WND::-3}_magnitude_topo15.nc"
    gmt grdsample ${ECMWF_WND::-3}_magnitude.nc -R$TOPO15_GRD_NC -G${ECMWF_WND::-3}_magnitude_topo15.nc
fi
```

### Optional step: Calculating wind direction
In addition (but not needed for this example and optional), you can calculate the wind direction using the equation 180/PI * atan2(-u, -v). In GMT, these steps would look like:
```bash
gmt grdmath ${ECMWF_WND::-3}_u.nc ${ECMWF_WND::-3}_v.nc ATAN2 180 D2R MUL = ${ECMWF_WND::-3}_direction_radians.nc
gmt grdedit ${ECMWF_WND::-3}_direction_radians.nc -D+z"Wind Direction [radians]"+r"180/pi*atan2(-u,-v)"
```

You can do the same for the direction in degrees: 
```bash
gmt grdmath ${ECMWF_WND::-3}_u.nc NEG ${ECMWF_WND::-3}_v.nc NEG ATAN2 180 D2R MUL R2D = ${ECMWF_WND::-3}_direction_degree.nc
gmt grdedit ${ECMWF_WND::-3}_direction_degree.nc -D+z"Wind Direction [degree]"+r"180/pi*atan2(-u,-v)"
```
*NOTE: If you didn't reverse the notation of the u and v component earlier, you will need to use
```
gmt grdmath ${ECMWF_WND::-3}_u.nc NEG ${ECMWF_WND::-3}_v.nc NEG ATAN2 180 D2R MUL = ${ECMWF_WND::-3}_direction_radians.nc
```
as the first step.*

# Ploting the data as vectors with a grayscale topography as background
First, we define a set of input variables for GMT (these will need to be adjusted for your purposes):
```
POSTSCRIPT_BASENAME=ECMWF-EI-WND_1999_2013_DJF_200_SAM
WIDTH=10
XSTEP=10
YSTEP=10
TITLE="ECMWF-WND DJF mean (1999-2013) - 200hPa"
POSTSCRIPT1=${POSTSCRIPT_BASENAME}_graytopo.ps
```
Next, we generate a colorscale as grayscale from -4000 to +4000 m in 250m steps:
```
DEM_CPT=relief_gray.cpt
gmt makecpt -T-4000/4000/250 -D -Cgray >$DEM_CPT
```
We also need a colorscale for the wind magnitude. Note that we know that the wind magnitude ranges from ~0 to ~30 and we set the range to 0-25 in 0.5 m/s steps.
```bash
WIND_CPT=wind_color.cpt
gmt makecpt -T0/25/0.5 -D -Cviridis >$WIND_CPT
```

It is also useful to define the vector scale. This is often a value you need to fine tune to best match your data. Here this is given in cm.
```bash
VECTSCALE=0.04c
```

Then we start plotting the various datasets. First, the topography:
```bash
gmt grdimage $TOPO15_GRD_NC -I$TOPO15_GRD_HS2_NC -JM$WIDTH -C$DEM_CPT -R${ECMWF_WND::-3}_u.nc -Q -Bx$XSTEP -By$YSTEP -BWSne+t"$TITLE" -Xc -Yc -E300 -K -P > $POSTSCRIPT1
```

Followed by international borders in gray and coastlines in black (we want to plot this first, because the wind vectors should be plotted on top of it):
```bash
gmt pscoast -W1/thin,black -R -J -N1/faint,gray -O -Df --FONT_ANNOT_PRIMARY=12p --FORMAT_GEO_MAP=ddd:mm:ssF -P -K >> $POSTSCRIPT1
```

Next, the wind vectors. You need to give the u and v components. We plot only every 8th vector in X and Y direction (`-Ix8`) because otherwise the data would be too dense. We set the scale of the colored arrowhead with `-Q0.25c+ba`. You have to adjust the vector scale, arrowhead size and vector spacing for an optimal figure
```bash
gmt grdvector -Gblack -S${VECTSCALE} -Q0.25c+ba -W0.5 ${ECMWF_WND::-3}_u.nc ${ECMWF_WND::-3}_v.nc -C$WIND_CPT -R -Ix8 -J -O -K -P >> $POSTSCRIPT1
```

Last, add the colorscale with label below the figure and convert to a PNG file:
```bash
psscale -R -J -DjBC+h+o-1.7c/-2.0c/+w5c/0.3c -C$WIND_CPT -F+gwhite+r1p+pthin,black -Baf -By+l"Wind Velocity (m/s)" --FONT=9p --FONT_ANNOT_PRIMARY=9p --MAP_FRAME_PEN=1 --MAP_FRAME_WIDTH=0.1 -O -P >> $POSTSCRIPT1
gmt psconvert $POSTSCRIPT1 -A -P -Tg
```
Additionally, you can use imagemagick to convert to a smaller file size JPG file:
```bash
convert -alpha off -quality 100 -density 150 $POSTSCRIPT1 ${POSTSCRIPT1::-3}.jpg
```

Resulting in a grayscale topographic background with colored wind vectors:
![ECMWF-EI-WND_1999_2013_DJF_200_SAM_graytopo.png](https://github.com/BodoBookhagen/GMT-plot-windvectors-SAM/raw/master/output_maps/ECMWF-EI-WND_1999_2013_DJF_200_SAM_graytopo.png)

# Ploting the data as vectors with a colored relief map as background
Following the previous explanations, we can generated a map with a colored background adjusting the parameters and using a different colorscale (`-Crelief`).
```bash
POSTSCRIPT_BASENAME=ECMWF-EI-WND_1999_2013_DJF_200_SAM
WIDTH=10
XSTEP=10
YSTEP=10

TITLE="ECMWF-WND DJF mean (1999-2013) - 200hPa"

POSTSCRIPT1=${POSTSCRIPT_BASENAME}_relieftopo.ps
DEM_CPT=relief_color.cpt
gmt makecpt -T-4000/4000/250 -D -Crelief >$DEM_CPT
VECTSCALE=0.04c
gmt grdimage $TOPO15_GRD_NC -I$TOPO15_GRD_HS_NC -JM$WIDTH -C$DEM_CPT -R${ECMWF_WND::-3}_u.nc -Q -Bx$XSTEP -By$YSTEP -BWSne+t"$TITLE" -Xc -Yc -E300 -K -P > $POSTSCRIPT1
gmt pscoast -W1/thin,black -R -J -N1/faint,gray -O -Df --FONT_ANNOT_PRIMARY=12p --FORMAT_GEO_MAP=ddd:mm:ssF -P -K >> $POSTSCRIPT1
gmt grdvector -Gblack -S${VECTSCALE} -Q0.3c+ba ${ECMWF_WND::-3}_u.nc ${ECMWF_WND::-3}_v.nc -C$WIND_CPT -R -Ix8 -J -O -K -P >> $POSTSCRIPT1
gmt psscale -R -J -DjBC+h+o-1.7c/-2.0c/+w5c/0.3c -C$WIND_CPT -F+gwhite+r1p+pthin,black -Baf -By+l"Wind Velocity (m/s)" --FONT=9p --FONT_ANNOT_PRIMARY=9p --MAP_FRAME_PEN=1 --MAP_FRAME_WIDTH=0.1 -O -P >> $POSTSCRIPT1
gmt psconvert $POSTSCRIPT1 -A -P -Tg
convert -alpha off -quality 100 -density 150 $POSTSCRIPT1 ${POSTSCRIPT1::-3}.jpg
```
![ECMWF-EI-WND_1999_2013_DJF_200_SAM_relieftopo.png](https://github.com/BodoBookhagen/GMT-plot-windvectors-SAM/raw/master/output_maps/ECMWF-EI-WND_1999_2013_DJF_200_SAM_relieftopo.png)

# Ploting the data as vectors with a colored wind velocities (hillshaded)
Following the previous explanations, we can generated a map showing wind magnitudes/velocites as background color.
```bash
POSTSCRIPT_BASENAME=ECMWF-EI-WND_1999_2013_DJF_200_SAM
WIDTH=10
XSTEP=10
YSTEP=10

TITLE="ECMWF-WND DJF mean (1999-2013) - 200hPa"

POSTSCRIPT1=${POSTSCRIPT_BASENAME}_windvelocity.ps
VECTSCALE=0.04c
gmt grdimage ${ECMWF_WND::-3}_magnitude_topo15.nc -I$TOPO15_GRD_HS_NC -JM$WIDTH -C$WIND_CPT -R${ECMWF_WND::-3}_u.nc -Q -Bx$XSTEP -By$YSTEP -BWSne+t"$TITLE" -Xc -Yc -E300 -K -P > $POSTSCRIPT1
gmt pscoast -W1/thin,black -R -J -N1/faint,gray -O -Df --FONT_ANNOT_PRIMARY=12p --FORMAT_GEO_MAP=ddd:mm:ssF -P -K >> $POSTSCRIPT1
gmt grdvector -Gblack -S${VECTSCALE} -Q0.25c+ba ${ECMWF_WND::-3}_u.nc ${ECMWF_WND::-3}_v.nc -R -Ix7 -J -O -K -P >> $POSTSCRIPT1
gmt psscale -R -J -DjBC+h+o-1.7c/-2.0c/+w5c/0.3c -C$WIND_CPT -F+gwhite+r1p+pthin,black -Baf -By+l"Wind Velocity (m/s)" --FONT=9p --FONT_ANNOT_PRIMARY=9p --MAP_FRAME_PEN=1 --MAP_FRAME_WIDTH=0.1 -O -P >> $POSTSCRIPT1
gmt psconvert $POSTSCRIPT1 -A -P -Tg
convert -alpha off -quality 100 -density 150 $POSTSCRIPT1 ${POSTSCRIPT1::-3}.jpg
```
![ECMWF-EI-WND_1999_2013_DJF_200_SAM_windvelocity.png](https://github.com/BodoBookhagen/GMT-plot-windvectors-SAM/raw/master/output_maps/ECMWF-EI-WND_1999_2013_DJF_200_SAM_windvelocity.png)

