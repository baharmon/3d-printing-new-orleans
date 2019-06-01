# Raster tiles

Set region
```
g.region n=536800 s=524800 e=3687000 w=3675000 res=2 save=region
```


Run the Python script `r.tile.extract.py`
to create and extract hexagonal tiles

Patch a selection of hexagonal tiles
```
r.patch input=hex_22,hex_20,hex_19,hex_18,hex_17,hex_15,hex_14,hex_13,hex_12,hex_10,hex_8,hex_5,hex_3 output=patch
```

Create vector and raster boundary
```
v.patch input=hex_3,hex_5,hex_8,hex_10,hex_12,hex_13,hex_14,hex_15,hex_17,hex_18,hex_19,hex_20,hex_22 output=region
v.clean -c input=region output=boundary tool=break,snap,rmdangle,chdangle,rmbridge,chbridge,rmdupl,rmdac,rmarea,rmline,rmsa
v.dissolve input=boundary output=region --overwrite
v.to.rast input=region output=region use=val
```

Create background raster
```
r.mapcalc --overwrite expression=mask = if(isnull(region),1,null())
r.colors -n map=mask color=grey1.0
```

Patch holes in digital surface model
```
r.mapcalc --overwrite expression="surface = if(isnull(region),null(),if(isnull(patch),9,patch))"
r.colors -e map=surface color=viridis
```

Remove temporary maps
```
g.remove -f type=raster name=patch
g.remove -f type=vector name=boundary
```

Model the river depth
```
r.lake --overwrite elevation=surface water_level=11 lake=river coordinates=3685975.78692,533168.038741
```

# Sea level rise

Create a new `slr` mapset
```
g.mapset -c mapset=slr location=lasspf_new_orleans
```

Add access to the `lidar` mapset
```
g.mapsets mapset=lidar
```

Copy rasters from lidar
```
g.copy raster=surface@lidar,surface
g.copy raster=mask@lidar,mask
g.copy raster=river@lidar,river
```

Use the Raster Digitizer to create multiple seeds for the flooding.
Create a new raster named `seeds` using `surface@lidar` as a background.

Model sea level rise scenarios
```
r.lake elevation=surface water_level=0.24 lake=sea_level_rise_24cm seed=seeds
r.lake elevation=surface water_level=0.63 lake=sea_level_rise_63cm seed=seeds
r.lake elevation=surface water_level=0.88 lake=sea_level_rise_88cm seed=seeds
r.lake elevation=surface water_level=2 lake=sea_level_rise_200cm seed=seeds
r.lake elevation=surface water_level=10 lake=sea_level_rise_1000cm seed=seeds
```

Install `r.lake.series` add-on module
```
g.extension extension=r.lake.series
```

Create space time raster dataset
```
t.create --overwrite output=slr semantictype=mean title=slr description=slr
```

Model sea level rise time series
```
r.lake.series elevation=surface@slr output=slr start_water_level=0.0 end_water_level=10.0 water_level_step=.1 seed_raster=seeds time_step=1 time_unit=years nproc=12
```

Alternative run of sea level rise time series
```
r.lake.series elevation=region output=slr start_water_level=1 end_water_level=10 water_level_step=.25 seed_raster=seeds@sealevelrise time_step=1 time_unit=years nproc=8
```

Animate sea level rise time series
```
g.gui.animation
```
