'''
Print some stats on all the elements we've found
'''

from utils.geo import ELEMENTS_FILENAME
import json
import operator

# Load the file
print 'Loading %s...' % ELEMENTS_FILENAME
with open(ELEMENTS_FILENAME, 'r') as f:
    elements = json.load(f)

#Total elements found: 

# Total = 1,435,427
print 'Total elements found: %d' % len(elements)

# Stats
sport_stats = {}
elements_stats = {}
for element in elements:
    element_type = element.get('type')

    # Find the most popular sport pitches
    if element_type == 'way':
        sport = element.get('tags', {}).get('sport', 'unknown').lower()
        sport_stats[sport] = (sport_stats[sport] + 1) \
            if sport in sport_stats else 1

    # Build type stats (nodes and ways)
    elements_stats[element_type] = (elements_stats[element_type] + 1) \
        if element_type in elements_stats else 1

# Elements stats: {u'node': 1,265,357, u'way': 170,070}
# Percentages, node: 88%, way: 12%
# About 7.5 nodes per way
print elements_stats

# Sort the sports by value, and reverse (descending values)
sport_stats = sorted(sport_stats.items(), key=operator.itemgetter(1))
sport_stats = list(reversed(sport_stats))

# Top 10:
# 1. baseball = 61,573 ways
# 2. tennis = 38,482 ways
# 3. soccer = 19,129 ways
# 4. basketball = 15,797 ways
# 5. unknown = 11,914 ways
# 6. golf = 6,826 ways
# 7. american_football = 6,266 ways
# 8. volleyball = 2,127 ways
# 9. multi = 1,423 ways
# 10. softball = 695 ways
for sport_stat in sport_stats[:10]:
    print sport_stat
