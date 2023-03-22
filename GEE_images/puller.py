from datetime import datetime
import glob
import time
import os
import ee
import re
import geemap
import numpy as np
import rasterio
import rasterio.mask
import warnings
from pyproj import CRS

from ee_datasets import get_image_period
from download import ee_export_image
from puller_helpers import get_polygon
from puller_helpers import mosaic_images
from puller_helpers import find_epsg 
from multi import multiprocess


# ee.Authenticate()
ee.Initialize()
warnings.filterwarnings("ignore")

# Initialize multiprocessing
MONTHS = ['01', '02', '03', '04', '05', '06', '07', '08',
          '09', '10', '11', '12']


def pull_year_image(year, poly, root, name, chunk_i, 
                    start, end, dataset, dst_crs):
    # See if pausing helpds with the time outs
    time.sleep(6)

    # Get image resolution
    if dataset == 'landsatSR':
        reso = 30
    if dataset == 'landsatTOA':
        reso = 15
    elif dataset =='sentinel':
        reso = 10

    out_path = os.path.join(
        root,
        str(year),
        '{}_{}_{}.tif'
    )
    image = get_image_period(year, start, end, poly, dataset)

    if not image.bandNames().getInfo():
        return None

    out = out_path.format(
        name,
        year,
        f'{start}_{end}_image_chunk_{chunk_i}'
    )

    _ = ee_export_image(
        image,
        filename=out,
        scale=reso,
        crs=dst_crs[0] + ':' + dst_crs[1],
        file_per_band=False
    )

    return out


def pull_images(polygon_path, root, river, 
                start, end, 
                start_year, end_year,
                dataset):

    if (start_year < 2017) and (dataset == 'sentinel'):
        raise ValueError('Sentinel does not have data before 2017')
    
    years = np.arange(start_year, end_year + 1)
    polys = get_polygon(polygon_path, root, dataset)

    # Get EPSG
    lon, lat = polys[0].getInfo()['coordinates'][0][0]
    dst_crs = find_epsg(lat, lon)

    # Pull the images
    year_root = os.path.join(root, river)
    os.makedirs(year_root, exist_ok=True)

    tasks = []
    for year_i, year in enumerate(years):
        for poly_i, poly in enumerate(polys):
            os.makedirs(
                os.path.join(
                    year_root, str(year),
                ), exist_ok=True
            )

            tasks.append((
                pull_year_image,
                (
                    year, poly, year_root, river, poly_i,
                    start, end, dataset, dst_crs
                )
            ))
    multiprocess(tasks)

    # Mosaic all the images
    out_paths = {}
    for year_i, year in enumerate(years):
        pattern = 'image'
        out_fp = mosaic_images(
            year_root, year, river, pattern, start, end
        )

        if not out_fp:
            continue

        out_paths[year] = out_fp

        year_dir = os.path.join(
            root,
            river,
            str(year)
        )
        os.rmdir(year_dir)

    return out_paths
