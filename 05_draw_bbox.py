'''
We're gonna use the bbox info from OSM to draw a box around the pitch, we
will use this box to better train our ML algo.
'''

from utils.geo import get_rectangle
from utils.geo import WAYS_DATA_FILENAME
import cv2
import json
import os

# We need the elements
# print 'Loading %s...' % WAYS_DATA_FILENAME
# with open(WAYS_DATA_FILENAME, 'r') as f:
#     ways_data = json.load(f)

image_files = [f for f in os.listdir('satellite') if f.endswith('.png')]
print len(image_files)

for image_file in image_files:
    print 'Processing %s...' % image_file
    # The ID is between the last underscore and the extension dot
    # For example: pitch_volleyball_268478401.png -> 268478401
    # way_id = image_file[image_file.rfind('_') + 1:image_file.find('.')]
    # bounds = ways_data[way_id]['bounds']

    # Add a rectangle with the feature
    # x, y, w, h = get_rectangle(bounds=bounds)
    # img = cv2.imread(os.path.join('satellite', image_file))
    # cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    # cv2.imwrite(os.path.join('satellite/rectangle', image_file), img)

    # To show the image
    # cv2.imshow('img',img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Generate a grayscale version
    img_gray = cv2.imread(os.path.join('satellite', image_file), 0)
    cv2.imwrite(os.path.join('satellite/gray', image_file), img_gray)
