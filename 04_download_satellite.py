'''
Usage:

    04_download_satellite.py [-h] [--sport SPORT] [--count COUNT]

    optional arguments:
      -h, --help     show this help message and exit
      --sport SPORT  Sport tag, for example: baseball, tennis, or soccer.
      --count COUNT  The total number of images to download.

For example:

    $ python 04_download_satellite.py --sport soccer --count 5
'''

from random import shuffle
from utils.geo import ELEMENTS_FILENAME, WAYS_DATA_FILENAME
from utils.mapbox_static import MapboxStatic
import argparse
import json

parser = argparse.ArgumentParser(add_help=True)

parser.add_argument('--sport',
    type=str, default='baseball',
    help='Sport tag, for example: baseball, tennis, or soccer.')
parser.add_argument('--count',
    type=int, default=5,
    help='The total number of images to download.')

args = vars(parser.parse_args())
count = args.get('count')
target_sport = args.get('sport')
print 'We are gonna download %d random pics of %s pitches.' \
    % (count, target_sport)

# We need the elements
print 'Loading %s...' % ELEMENTS_FILENAME
with open(ELEMENTS_FILENAME, 'r') as f:
    elements = json.load(f)

# We need the elements
print 'Loading %s...' % WAYS_DATA_FILENAME
with open(WAYS_DATA_FILENAME, 'r') as f:
    ways_data = json.load(f)

# Randomize elements list to make sure we don't download all pics from the
# same sample
shuffle(elements)

# Now we're gonna download the satellite images for these locations
mapbox_static = MapboxStatic(
    namespace='pitch',
    root_folder='satellite')

total_downloaded = 0
for element in elements:
    # They're strings in the dict now
    element_id_str = unicode(element.get('id'))
    sport = element.get('tags', {}).get('sport', 'unknown').lower()
    if element_id_str in ways_data and sport == target_sport:
        if total_downloaded >= count:
            break
        print '> Element: %s (%s)' % (element.get('id'), sport)
        url = mapbox_static.get_url(
            latitude=ways_data[element_id_str].get('lat'),
            longitude=ways_data[element_id_str].get('lon'))
        print url
        element_id_sport = '%s_%s' % (sport, element_id_str)
        success = mapbox_static.download_tile(
            element_id=element_id_sport,
            url=url)
        if success:
            total_downloaded += 1
