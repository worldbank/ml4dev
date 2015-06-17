from shapely.geometry import Polygon
import json
import os

WAYS_DATA_FILENAME = 'ways_data.json'


def get_ways_data(elements, coords):
    # Get cached version if available
    if os.path.isfile(WAYS_DATA_FILENAME):
        with open(WAYS_DATA_FILENAME, 'r') as f:
            ways_data = json.load(f)
        print 'get_ways_data: loaded cached file.'
        return ways_data

    # Go through the ways, build the polygon, and compute the centroid that we'll
    # use to download the mapbox satellite image
    print 'get_ways_data: computing...'
    ways_data = {}
    for element in elements:
        # Only process ways
        if element.get('type') != 'way':
            continue
        # Only process ways with 3 or more nodes
        # Otherwise, Shapely will complain
        nodes = element.get('nodes')
        if len(nodes) < 3:
            continue
        exterior = [(coords[node].get('lat'), coords[node].get('lon')) \
            for node in nodes]
        # Build the polygon and compute its bbox and centroid
        way_polygon = Polygon(exterior)
        ways_data[element.get('id')] = {
            'bounds': way_polygon.bounds,
            'lat': way_polygon.centroid.x,
            'lon': way_polygon.centroid.y}

    # Cache the file
    with open(WAYS_DATA_FILENAME, 'w') as f:
        json.dump(ways_data, f, indent=2)

    # Done
    return ways_data
