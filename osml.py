'''
We're gonna download every pitch in the US (leisure=pitch) that is defined
as a way (we want to be able to compute a bounding box and centroid to
improve the CV analysis).
'''

from random import shuffle
from shapely.geometry import Polygon
from utils.mapbox_static import MapboxStatic
from utils.overpass_client import OverpassClient
import json
import numpy as np
import operator
import os

def get_ql_text(bb_s, bb_w, bb_n, bb_e):
    # The operator (._;>;); asks for the nodes and ways that are referred by
    # the relations and ways in the result.
    ql_pitch = '''\
    way
      [leisure=pitch]
      ({bb_s},{bb_w},{bb_n},{bb_e});
    (._;>;);
    out;
    '''
    return ql_pitch.format(bb_s=bb_s, bb_w=bb_w, bb_n=bb_n, bb_e=bb_e)

# For the continental US bbox we use the one provided by:
# https://www.flickr.com/places/info/24875662
us_s = 24.9493
us_w = -125.0011
us_n = 49.5904
us_e = -66.9326

# In charge of querying the OSM DB
overpass_client = OverpassClient()

# Overpass requires a bbox in the SWNE format. Because the continental US is
# too big for a single query (it timeouts), we're gonna split in a smaller
# queries. This means (samples-1)^2 boxes.
samples = 6  # 25 boxes
lat_range = np.linspace(us_s, us_n, num=samples)
lon_range = np.linspace(us_w, us_e, num=samples)

elements = []
for lat_index in range(samples - 1):
    for lon_index in range(samples - 1):
        bb_s = lat_range[lat_index]
        bb_n = lat_range[lat_index + 1]
        bb_w = lon_range[lon_index]
        bb_e = lon_range[lon_index + 1]
        ql_text = get_ql_text(bb_s=bb_s, bb_w=bb_w, bb_n=bb_n, bb_e=bb_e)
        # Safe to run multimple times, results are cached
        result = overpass_client.query(ql_text=ql_text)
        partial_elements = result.get('elements', [])
        print 'Partials elements found: %d' % len(partial_elements)
        elements += partial_elements

# I ran some stats. Total elements: 1434747
# Total nodes = 1264725 (88%), total ways = 170022 (12%)
# About 7.5 nodes per way.
print 'Total elements found: %d' % len(elements)

# Randomize elements list to make sure we don't download all pics from the
# same sample
shuffle(elements)

# sport_stats = {}
# elements_stats = {}
coords = {}

for element in elements:
    element_type = element.get('type')

    # Find the most popular sport pitches
    # if element_type == 'way':
    #     sport = element.get('tags', {}).get('sport', 'unknown').lower()
    #     sport_stats[sport] = (sport_stats[sport] + 1) \
    #         if sport in sport_stats else 1

    # Build type stats (nodes and ways)
    # elements_stats[element_type] = (elements_stats[element_type] + 1) \
    #     if element_type in elements_stats else 1

    # Store node coords for later
    if element_type == 'node':
        element_id = element.get('id')
        coords[element_id] = {
            'lat': element.get('lat'),
            'lon': element.get('lon')}

# Sort sports by count (second element)
# This is the top 10 (removed unknown, which it'd be 5th)
# 1. baseball -- 61555 ways
# 2. tennis -- 38475 ways
# 3. soccer -- 19117 ways
# 4. basketball -- 15794 ways
# 5. golf -- 6819 ways
# 6. american_football -- 6265 ways
# 7. volleyball -- 2127 ways
# 8. multi -- 1423 ways
# 9. softball -- 695 ways
# 10. skateboard -- 662 ways
# sorted_sport_stats = sorted(sport_stats.items(), key=operator.itemgetter(1))
# print sorted_sport_stats

# Go through the ways, build the polygon, and compute the centroid that we'll
# use to download the mapbox satellite image
if os.path.isfile('ways_data.json'):
    with open('ways_data.json', 'r') as f:
        ways_data = json.load(f)
else:
    print 'Doing geo...'
    ways_data = {}
    for element in elements:
        element_type = element.get('type')
        if element_type == 'way':
            nodes = element.get('nodes')
            if len(nodes) >= 3:
                exterior = [(coords[node].get('lat'), coords[node].get('lon')) \
                    for node in nodes]
                way_polygon = Polygon(exterior)
                element_id = element.get('id')
                ways_data[element_id] = {
                    'bounds': way_polygon.bounds,
                    'lat': way_polygon.centroid.x,
                    'lon': way_polygon.centroid.y}
    with open('ways_data.json', 'w') as f:
        json.dump(ways_data, f, indent=2)

# Now we're gonna download the satellite images for these locations
mapbox_static = MapboxStatic(
    namespace='pitch',
    root_folder='satellite')

sport_limit = 10
sport_count = {
    'baseball': 0,
    'tennis': 0,
    'soccer': 0,
    'basketball': 0,
    'american_football': 0}

for element in elements:
    # They're strings in the dict now
    element_id_str = unicode(element.get('id'))
    sport = element.get('tags', {}).get('sport', 'unknown').lower()
    if element_id_str in ways_data and sport in sport_count:
        sport_count[sport] += 1
        if sport_count[sport] <= sport_limit:
            print '> Element: %s (%s)' % (element.get('id'), sport)
            url = mapbox_static.get_url(
                latitude=ways_data[element_id_str].get('lat'),
                longitude=ways_data[element_id_str].get('lon'))
            print url
            element_id_sport = '%s_%s' % (sport, element_id_str)
            mapbox_static.download_tile(
                element_id=element_id_sport,
                url=url)
