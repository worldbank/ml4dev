from __future__ import division
import csv
import cv2
import numpy as np
import os

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
    img = cv2.imread(filename, 0)
    pitches = tennis_cascade.detectMultiScale(
        img, minNeighbors=min_neighbors)
    return len(pitches)

for tennis_cascade_file in tennis_cascade_files:
    print tennis_cascade_file
    tennis_cascade = cv2.CascadeClassifier(tennis_cascade_file)

    # Open
    positive_f = open(tennis_cascade_file[:-4] + '_positive.csv', 'w')
    negative_f = open(tennis_cascade_file[:-4] + '_negative.csv', 'w')
    positive_writer = csv.writer(positive_f)
    negative_writer = csv.writer(negative_f)

    for min_neighbors in range(0, 501, 10):
        print min_neighbors

        # Pos
        total_set = 0
        for positive_file in positive_files:
            total_pitches = get_total_pitches(
                tennis_cascade=tennis_cascade,
                filename=positive_file,
                min_neighbors=min_neighbors)
            total_set += total_pitches
        total_average = total_set / len(positive_files)
        positive_writer.writerow([total_average, min_neighbors])

        # Neg
        total_set = 0
        for negative_file in negative_files:
            total_pitches = get_total_pitches(
                tennis_cascade=tennis_cascade,
                filename=negative_file,
                min_neighbors=min_neighbors)
            total_set += total_pitches
        total_average = total_set / len(negative_files)
        negative_writer.writerow([total_average, min_neighbors])

    # Close
    positive_f.close()
    negative_f.close()
