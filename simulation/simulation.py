"""
Wrapper/Helper script for Leeway simulations with OpenDrift.

Use it with the docker container by mounting a directory and copying the file to it:

    docker run -it --volume ./workdir:/code/leeway opendrift/opendrift python3 leeway/simulation.py --longitude 11.9545 --latitude 35.2966 --start-time "2022-12-05 03:00" --duration 12
"""
import argparse
import uuid
import os

from datetime import datetime, timedelta

from opendrift.models.leeway import Leeway

from opendrift.readers import reader_netCDF_CF_generic
from opendrift.readers import reader_global_landmask

PARSER = argparse.ArgumentParser(description='Simulate drift of object')
PARSER.add_argument('--longitude',
                    help="Start longitude of the drifting object")
PARSER.add_argument('--latitude',
                    help="Start latitude of the drifting object")
PARSER.add_argument('--start-time',
                    help='Starting time (YYYY-MM-DD HH:MM) of the simulation. Default: Now',
                    default=datetime.now().strftime('%Y-%m-%d %H:%M'))
PARSER.add_argument('--duration',
                    help='Duration of the simulation in hours. Default: 12h.',
                    default=12)
PARSER.add_argument('--object-type',
                    help='Object type integer ID from https://github.com/OpenDrift/opendrift/blob/master/opendrift/models/OBJECTPROP.DAT',
                    default=27)
PARSER.add_argument('--id',
                    help='ID used for result image name.',
                    default=str(uuid.uuid4()))
ARGS = PARSER.parse_args()

o = Leeway(loglevel=50)

o.add_readers_from_list(['https://tds.hycom.org/thredds/dodsC/GLBy0.08/latest',
                         'https://pae-paha.pacioos.hawaii.edu/thredds/dodsC/ncep_global/NCEP_Global_Atmospheric_Model_best.ncd'],
                        lazy=False)

reader_landmask = reader_global_landmask.Reader(extent=[0, 0, 360, 90])
o.add_reader([reader_landmask])

o.seed_elements(lon=float(ARGS.longitude),
                lat=float(ARGS.latitude),
                time=datetime.strptime(ARGS.start_time, '%Y-%m-%d %H:%M'),
                number=100, radius=1000,
                object_type=ARGS.object_type)

o.run(duration=timedelta(hours=int(ARGS.duration)), time_step=600)

o.plot(fast=True, legend=True, filename=os.path.join("/code", "leeway", ARGS.id))
