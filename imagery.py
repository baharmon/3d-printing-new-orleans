#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@brief: script for processing imagery in GRASS GIS

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
dirpath = os.path.normpath(r"Job405228_2016_NGS_NaturalColorImagery")

# set variables
res = 2

def main():

    imagery()
    atexit.register(cleanup)
    sys.exit(0)

def imagery():
    """import composite, and patch imagery"""

# import all imagery
for root, dirs, files in os.walk(dirpath):
    i = 1
    for file in files:
        if file.endswith(".tif"):
            rootpath = os.path.join(dirpath,root)
            filepath = os.path.join(rootpath,file)

            # import imagery
            gscript.run_command('r.in.gdal',
                input=filepath,
                output='imagery_'+str(i),
                title='imagery_'+str(i),
                flags='ek',
                memory=9000,
                overwrite=overwrite)

            # composite true color rasters
            gscript.run_command('r.composite',
                red='imagery_'+str(i)+'.1',
                green='imagery_'+str(i)+'.2',
                blue='imagery_'+str(i)+'.3',
                output='imagery_'+str(i),
                overwrite=overwrite)

            i = i + 1
        else:
            pass

    # remove temporary maps
    try:
        gscript.run_command('g.remove',
            type='raster',
            pattern='*.*',
            flags='f')
    except CalledModuleError:
        pass

    # list imagery rasters
    imagery_list = gscript.list_grouped('rast',
        pattern='imagery*')[mapset]

    # set region
    gscript.run_command('g.region',
        raster=imagery_list,
        res=res)

    # patch imagery rasters
    gscript.run_command('r.patch',
        input=imagery_list,
        output='imagery_2016',
        overwrite=overwrite)


def cleanup():

    pass

    # # remove temporary maps
    # try:
    #     gscript.run_command('g.remove',
    #         type='raster',
    #         pattern='imagery_*',
    #         exclude='*2016',
    #         flags='f')
    # except CalledModuleError:
    #     pass


if __name__ == "__main__":
    atexit.register(cleanup)
    sys.exit(main())
