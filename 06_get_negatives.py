'''
Let's download a few negative images to train the algo.

Usage:
    python 06_get_negatives.py [-h] [--count COUNT]

    optional arguments:
      -h, --help     show this help message and exit
      --count COUNT  The total number of negative images to download.
'''

from random import shuffle
from utils.geo import ELEMENTS_FILENAME
from utils.mapbox_static import MapboxStatic
import argparse
import json
import random

parser = argparse.ArgumentParser(add_help=True)

parser.add_argument('--count',
    type=int, default=5,
    help='The total number of negative images to download.')

args = vars(parser.parse_args())
count = args.get('count')
print 'We are gonna download %d negative images' % count

# We need the elements
print 'Loading %s...' % ELEMENTS_FILENAME
with open(ELEMENTS_FILENAME, 'r') as f:
    elements = json.load(f)

# Randomize elements list to make sure we don't download all pics from the
# same sample. Then cut it.
shuffle(elements)

# Now we're gonna download the satellite images for these locations
mapbox_static = MapboxStatic(
    namespace='negative',
    root_folder='satellite/negative')

total_downloaded = 0
for element in elements:
    if total_downloaded >= count:
            break
    if element.get('type') != 'node':
        continue
    # Move the latlon a random amount, random() is in the range [0.0, 1.0)
    target_lat = element.get('lat') + (random.random() - 0.5)
    target_lon = element.get('lon') + (random.random() - 0.5)
    url = mapbox_static.get_url(latitude=target_lat, longitude=target_lon)
    print url
    success = mapbox_static.download_tile(
        element_id=element.get('id'),
        url=url)
    if success:
        total_downloaded += 1
