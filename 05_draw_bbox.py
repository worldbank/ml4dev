'''
We're gonna use the bbox info from OSM to draw a box around the pitch, we
will use this box to better train our ML algo.
'''

from utils.geo import WAYS_DATA_FILENAME
import cv2
import json
import math
import os

image_width = 1280
image_height = 1280

def get_rectangle(bounds):
    # This converts a latitude delta into an image delta. For USA, at zoom
    # level 19, we know that we have 0.21 meters/pixel. So, an image is showing
    # about 1280 pixels * 0.21 meters/pixel = 268.8 meters.
    # On the other hand we know that at the same angle, a degress in latlon is:
    # https://en.wikipedia.org/wiki/Latitude
    # latitude = 111,132 m
    # longitude = 78,847 m
    # Finally, we add 5% to make sure the feature is contained within the
    # rectangle (from what we see, the bbox are tight around the feature)
    latitude_factor  = 1.05 * 111132.0 / 0.21
    longitude_factor = 1.05 * 78847.0 / 0.21

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
    if x == 0 or y == 0 or w == 0 or h == 0:
        print '** Warning ** There is something wrong with this image bounds.'
        print bounds
        print x, y, w, h
    return x, y, w, h

# We need the elements
print 'Loading %s...' % WAYS_DATA_FILENAME
with open(WAYS_DATA_FILENAME, 'r') as f:
    ways_data = json.load(f)

image_files = [f for f in os.listdir('satellite') if f.endswith('.png')]

for image_file in image_files:
    print 'Processing %s...' % image_file
    # The ID is between the last underscore and the extension dot
    # For example: pitch_volleyball_268478401.png -> 268478401
    way_id = image_file[image_file.rfind('_') + 1:image_file.find('.')]
    bounds = ways_data[way_id]['bounds']

    # Add a rectangle with the feature
    x, y, w, h = get_rectangle(bounds=bounds)
    img = cv2.imread(os.path.join('satellite', image_file))
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    cv2.imwrite(os.path.join('satellite/rectangle', image_file), img)

    # Generate a grayscale version
    img_gray = cv2.imread(os.path.join('satellite', image_file), 0)
    cv2.imwrite(os.path.join('satellite/gray', image_file), img_gray)

# To show the image
# cv2.imshow('img',img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
