'''
We're gonna download every pitch in the US (leisure=pitch) that is defined
as a way (we want to be able to compute a bounding box and centroid to
improve the CV analysis).
'''

from utils.overpass_client import OverpassClient

ELEMENTS_FILENAME = 'data/elements.json'

# The operator (._;>;); asks for the nodes and ways that are referred by
# the relations and ways in the result.
ql_pitch = '''\
way
  [leisure=pitch]
  ({query_bb_s},{query_bb_w},{query_bb_n},{query_bb_e});
(._;>;);
out;
'''

# For the continental US bbox we use the one provided by:
# https://www.flickr.com/places/info/24875662
us_s = 24.9493
us_w = -125.0011
us_n = 49.5904
us_e = -66.9326

# Overpass requires a bbox in the SWNE format. Because the continental US is
# too big for a single query (it timeouts), we're gonna split in a smaller
# queries. This means (samples-1)^2 boxes.
samples = 11  # 100 boxes

# I ran some stats. Total elements: 1,434,747
# Total nodes = 1,264,725 (88%), total ways = 170,022 (12%)
# About 7.5 nodes per way.
overpass_client = OverpassClient()
elements = overpass_client.get_bbox_elements(
    ql_template=ql_pitch,
    bb_s=us_s, bb_w=us_w, bb_n=us_n, bb_e=us_e,
    samples=samples)
print 'Total elements found: %d' % len(elements)

# Cache the result
with open(ELEMENTS_FILENAME, 'w') as f:
    json.dump(elements, f)
