from shapely.geometry import Polygon
import math

image_width = 1280
image_height = 1280

ELEMENTS_FILENAME = 'data/elements.json'
WAYS_DATA_FILENAME = 'data/ways.json'

# Go through the ways, build the polygon, and compute the centroid that we'll
# use to download the mapbox satellite image
def get_ways_data(elements, coords):
    ways_data = {}
    for element in elements:
        # Only process ways
        if element.get('type') != 'way':
            continue
        # Only process ways with 3 or more nodes, otherwise
        # Shapely will complain.
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

    # Done
    return ways_data

def get_rectangle(bounds):
    # This converts a latitude delta into an image delta. For USA, at zoom
    # level 19, we know that we have 0.21 meters/pixel. So, an image is showing
    # about 1280 pixels * 0.21 meters/pixel = 268.8 meters.
    # On the other hand we know that at the same angle, a degress in latlon is:
    # https://en.wikipedia.org/wiki/Latitude
    # latitude = 111,132 m
    # longitude = 78,847 m
    latitude_factor  = 111132.0 / 0.21
    longitude_factor = 78847.0 / 0.21

    # Feature size
    feature_width = longitude_factor * math.fabs(bounds[1] - bounds[3])
    feature_height = latitude_factor * math.fabs(bounds[0] - bounds[2])
    if feature_width > image_width or feature_height > image_height:
        print '** Warning ** The feature is bigger than the image.'

    # CV params (int required)
    x = int((image_width / 2) - (feature_width / 2))
    y = int((image_height / 2) - (feature_height / 2))
    w = int(feature_width)
    h = int(feature_height)
    if w <= 25 or h <= 25:
        print '** Warning ** This image has very narrow bounds.'
        print bounds
        print x, y, w, h
    if x <= 0 or y <= 0 or w <= 0 or h <= 0:
        print '** Warning ** There is something wrong with this image bounds.'
        print bounds
        print x, y, w, h
    return x, y, w, h
