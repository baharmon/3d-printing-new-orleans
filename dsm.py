#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@brief: script for processing the 2012 USACE New Orleans rasters in GRASS GIS

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.

@author: Brendan Harmon (brendanharmon@gmail.com)
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

# set directory
dirpath = os.path.normpath(r"Job404676_la2012_usace_new_orleans_m6350")

# set variables
res = 2

def main():

    dsm()
    atexit.register(cleanup)
    sys.exit(0)

def dsm():
    """import and patch digital surface models"""

    # import all dsm
    for root, dirs, files in os.walk(dirpath):
        i = 1
        for file in files:
            if file.endswith(".tif"):
                rootpath = os.path.join(dirpath,root)
                filepath = os.path.join(rootpath,file)

                # import dsm tiles
                gscript.run_command('r.in.gdal',
                    input=filepath,
                    output='dsm_'+str(i),
                    title='dsm_'+str(i),
                    flags='ek',
                    memory=9000,
                    overwrite=overwrite)

                i = i + 1

            else:
                pass

        # list dsm rasters
        dsm_list = gscript.list_grouped('rast',
            pattern='dsm*')[mapset]

        # set region
        gscript.run_command('g.region',
            raster=dsm_list,
            res=res)

        # patch dsm rasters
        gscript.run_command('r.patch',
            input=dsm_list,
            output='surface_2012',
            overwrite=overwrite)

def cleanup():

    # remove temporary maps
    try:
        gscript.run_command('g.remove',
            type='raster',
            pattern='dsm_*',
            flags='f')
    except CalledModuleError:
        pass

if __name__ == "__main__":
    atexit.register(cleanup)
    sys.exit(main())
