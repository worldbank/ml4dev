from __future__ import division
import cv2
import os

# Threshold
min_neighbors = 1750
print min_neighbors

tennis_cascade_files = [
    'output/cascade-default.xml',
    'output/cascade-4000-2000.xml',
    'output/cascade-6000-3000.xml',
    'output/cascade-8000-4000.xml']

positive_files = [os.path.join('satellite/fit', f) \
    for f in os.listdir('satellite/fit') if f.endswith('.png')]

negative_files = [os.path.join('satellite/fit/negative', f) \
    for f in os.listdir('satellite/fit/negative') if f.endswith('.png')]

def get_total_pitches(tennis_cascade, filename, min_neighbors):
    img = cv2.imread(filename)
    gray = cv2.imread(filename, 0)
    if 'negative' in filename:
        target = filename.replace(
            'satellite/fit/negative',
            'satellite/fit/negative/bbox')
    else:
        target = filename.replace(
            'satellite/fit',
            'satellite/fit/bbox')
    pitches = tennis_cascade.detectMultiScale(
        gray, minNeighbors=min_neighbors)
    for (x,y,w,h) in pitches:
        if 'negative' in filename:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),5)
        else:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),5)
    cv2.imwrite(target, img)
    return len(pitches)

tennis_cascade_file = tennis_cascade_files[3]
tennis_cascade = cv2.CascadeClassifier(tennis_cascade_file)
print tennis_cascade_file

total_files = 100

# Pos
pos_success = 0
for positive_file in positive_files[:total_files]:
    print positive_file
    total_pitches = get_total_pitches(
        tennis_cascade=tennis_cascade,
        filename=positive_file,
        min_neighbors=min_neighbors)
    if total_pitches >= 1:
        pos_success += 1

# Neg
neg_success = 0
for negative_file in negative_files[:total_files]:
    print negative_file
    total_pitches = get_total_pitches(
        tennis_cascade=tennis_cascade,
        filename=negative_file,
        min_neighbors=min_neighbors)
    if total_pitches < 1:
        neg_success += 1
    else:
        print '** negative file %s has %s pitches **' % (
            negative_file, total_pitches)

pos_percentage = 100 * pos_success / total_files
neg_percentage = 100 * neg_success / total_files
print 'pos_percentage = %s' % pos_percentage
print 'neg_percentage = %s' % neg_percentage
