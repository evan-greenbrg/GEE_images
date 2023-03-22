import argparse
import platform

import ee
from multiprocessing import set_start_method
from puller import pull_images


def main(poly, dataset, start, end, start_year, end_year, out, river):

    print("Pulling Images")
    paths = pull_images(
        poly,
        out,
        river,
        start,
        end,
        int(start_year),
        int(end_year),
        dataset
    )

    return True

if __name__ == '__main__':
    if platform.system() == "Darwin":
        set_start_method('spawn')

    ee.Initialize()

    parser = argparse.ArgumentParser(description='Pull Mobility')
    parser.add_argument('--poly', metavar='poly', type=str,
                        help='In path for the geopackage path')

    parser.add_argument('--dataset', metavar='dataset', type=str,
                        choices=['landsatSR', 'landsatTOA', 'sentinel'],
                        help='what is the GEE data source')

    parser.add_argument('--start', metavar='start', type=str,
                        help='Start month-day in format: MO-DAY'
                        )

    parser.add_argument('--end', metavar='end', type=str,
                        help='End month-day in format: MO-DAY'
                        )

    parser.add_argument('--start_year', metavar='start_year', type=str,
                        help='Start year'
                        )

    parser.add_argument('--end_year', metavar='end_year', type=str,
                        help='End year'
                        )

    parser.add_argument('--out', metavar='out', type=str,
                        help='output root directory')

    parser.add_argument('--river', metavar='r', type=str,
                        help='River name')

    args = parser.parse_args()

    main(
        args.poly, 
        args.dataset,
        args.start, 
        args.end, 
        args.start_year, 
        args.end_year, 
        args.out, 
        args.river
    )
