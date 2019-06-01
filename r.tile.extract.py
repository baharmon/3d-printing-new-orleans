#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AUTHOR:    Brendan Harmon <brendan.harmon@gmail.com>

PURPOSE:   Extract raster tiles in GRASS GIS

COPYRIGHT: (C) 2019 Brendan Harmon

LICENSE:   This program is free software under the GNU General Public
           License (>=v2).
"""

import os
import sys
import atexit
import grass.script as gscript
from grass.exceptions import CalledModuleError

# temporary region
gscript.use_temp_region()

# set environment
env = gscript.gisenv()
overwrite = True
env['GRASS_OVERWRITE'] = overwrite
env['GRASS_VERBOSE'] = False
env['GRASS_MESSAGE_FORMAT'] = 'standard'
gisdbase = env['GISDBASE']
location = env['LOCATION_NAME']
mapset = env['MAPSET']

# set parameters
grid='hex'
cell='hex'
raster='surface_2012'
rows=5
columns=5


def main():
    """Extract tiles of raster data from vector grid"""

    make_grid()
    info = extract_tiles()
    export_tiles(info)
    atexit.register(cleanup)
    sys.exit(0)


def make_grid():
    """Generate vector grid"""

    # Make vector grid
    gscript.run_command('v.mkgrid',
    map=grid,
    grid=[rows,columns],
    flags='h',
    overwrite=overwrite)

def extract_tiles():
    """Extract tiles of raster data from vector grid"""

    # determine number of areas in vector grid
    info = gscript.parse_command('v.info',
        map=grid,
        flags='t')
    # extract each grid cell from vector grid
    for i in xrange(1, int(info['areas'])+1):
        gscript.run_command('v.extract',
            input=grid,
            cats=i,
            output=cell+'_'+str(i),
            overwrite=overwrite)
        # set mask to cell
        gscript.run_command('r.mask',
            vector=cell+'_'+str(i),
            overwrite=overwrite)
        #  write raster tile
        gscript.run_command('r.mapcalc',
            expression='{output} = {raster}'.format(output=cell+'_'+str(i),
                raster=raster),
            overwrite=overwrite)
        # remove mask
        gscript.run_command('r.mask',
            flags='r')
    return info


def export_tiles(info):
    """Export tiles of raster data extracted from grid"""

    # export raster tiles as geotiff
    for i in xrange(1, int(info['areas'])+1):
        gscript.run_command('r.out.gdal',
            input=cell+'_'+str(i),
            output=os.path.join(gisdbase, location, cell+'_'+str(i)+'.tif'),
            overwrite=overwrite)


def cleanup():
    try:
        # remove mask
        gscript.run_command('r.mask',
            flags='r')
    except CalledModuleError:
        pass


if __name__ == "__main__":
    atexit.register(cleanup)
    sys.exit(main())
