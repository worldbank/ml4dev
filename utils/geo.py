from shapely.geometry import Polygon

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
