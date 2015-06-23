from utils.geo import get_rectangle
from utils.geo import WAYS_DATA_FILENAME
import json
import os

# We need the elements
print 'Loading %s...' % WAYS_DATA_FILENAME
with open(WAYS_DATA_FILENAME, 'r') as f:
    ways_data = json.load(f)

samples_data = {}

image_files = [f for f in os.listdir('satellite/gray') if f.endswith('.png')]
for image_file in image_files:
    print 'Processing %s...' % image_file

    # Find the category
    sport = image_file[image_file.find('_')+1:image_file.rfind('_')]
    if sport not in samples_data:
        samples_data[sport] = []

    # The ID is between the last underscore and the extension dot
    # For example: pitch_volleyball_268478401.png -> 268478401
    way_id = image_file[image_file.rfind('_') + 1:image_file.find('.')]
    bounds = ways_data[way_id]['bounds']

    # Add a rectangle with the feature
    x, y, w, h = get_rectangle(bounds=bounds)
    if w <= 25 or h <= 25:
        print 'Pic not added'
        continue
    if x <= 0 or y <= 0 or w <= 0 or h <= 0:
        print 'Pic not added'
        continue
    entry = 'satellite/gray/%s\t1\t%d\t%d\t%d\t%d\n' % (image_file, x, y, w, h)
    samples_data[sport].append(entry)

for sport in samples_data.keys():
    datafile = 'info_%s.dat' % sport
    print 'Saving data file: %s' % datafile
    with open(datafile, 'w') as f:
        print len(samples_data[sport])
        for entry in samples_data[sport]:
            f.write(entry)
