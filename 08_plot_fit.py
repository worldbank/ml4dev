import csv
import matplotlib.pyplot as plt

csv_files = {
    '4000_negative': 'fit/cascade-4000-2000_negative.csv',
    '4000_positive': 'fit/cascade-4000-2000_positive.csv',
    '6000_negative': 'fit/cascade-6000-3000_negative.csv',
    '6000_positive': 'fit/cascade-6000-3000_positive.csv',
    '8000_negative': 'fit/cascade-8000-4000_negative.csv',
    '8000_positive': 'fit/cascade-8000-4000_positive.csv',
    '2000_negative': 'fit/cascade-default_negative.csv',
    '2000_positive': 'fit/cascade-default_positive.csv'}

cases = ['2000', '4000', '6000', '8000']

for case in cases:
    with open(csv_files[case + '_positive'], 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        values = [row for row in csv_reader]
        y_pos_values = [entry[0] for entry in values]
        x_pos_values = [entry[1] for entry in values]
        
    with open(csv_files[case + '_negative'], 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        values = [row for row in csv_reader]
        y_neg_values = [entry[0] for entry in values]
        x_neg_values = [entry[1] for entry in values]

    plt.clf()
    plt.plot(x_pos_values, y_pos_values, color='b', label='positives')
    plt.plot(x_neg_values, y_neg_values, color='r', label='negatives')
    plt.plot([0, 500], [1, 1], color='g', linestyle='--')
    plt.axis([0, 500, 0, 10])  # [xmin, xmax, ymin, ymax]
    plt.xlabel('min neighbors')
    plt.ylabel('pitches')
    plt.title('Finding the optimum min neighbors value')
    plt.legend()
    plt.grid(True)
    plt.savefig('fit/cascade-%s.png' % case)
