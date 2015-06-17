from utils.geo import ELEMENTS_FILENAME, WAYS_DATA_FILENAME
from utils.geo import get_ways_data
import json
import operator

# We need the elements
print 'Loading %s...' % ELEMENTS_FILENAME
with open(ELEMENTS_FILENAME, 'r') as f:
    elements = json.load(f)

# And we need the coordinates for all the nodes
coords = {}
for element in elements:
    if element.get('type') == 'node':
        element_id = element.get('id')
        coords[element_id] = {
            'lat': element.get('lat'),
            'lon': element.get('lon')}

# Now we can get the dict
print 'Building %s...' % WAYS_DATA_FILENAME
ways_data = get_ways_data(elements=elements, coords=coords)

# Finally, cache the file
with open(WAYS_DATA_FILENAME, 'w') as f:
    json.dump(ways_data, f)
