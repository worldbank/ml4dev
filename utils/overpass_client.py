from restwice import RestClient
from restwice import MemcacheLocal
import numpy as np

ENDPOINT = 'http://overpass-api.de/api/interpreter'
MEMCACHE_NAMESPACE = 'overpass'
REQUESTS_TIMEOUT = 60 * 5  # 5 minutes


class OverpassClient(object):
    def __init__(self):
        self._rest_client = RestClient()
        self._rest_client.set_endpoint(endpoint=ENDPOINT)

        # Set better timeout value
        self._client_settings = {'timeout': REQUESTS_TIMEOUT}

        # Set local caching
        memcache_client = MemcacheLocal(root_folder='_cache_overpass')
        self._rest_client.enable_cache(
            memcache_client=memcache_client,
            memcache_namespace=MEMCACHE_NAMESPACE)

    def _get_data(self, ql_text=None):
        return '[out:json];' + ql_text

    def do_query(self, ql_text=None):
        data = self._get_data(ql_text=ql_text)
        self._rest_client.set_data(data={'data': data})
        result, _ = self._rest_client.do_get(
            json_response=True,
            json_request=False,
            client_settings=self._client_settings)
        return result

    def get_bbox_elements(self, ql_template, bb_s, bb_w, bb_n, bb_e, samples=2):
        # Samples subdivides the bbox into smaller bboxes to make sure the
        # request doesn't timeout. For linspace below to work, we need this
        # number to be 2 or greater.
        assert samples >= 2

        # Track iterations
        total_iterations = (samples - 1) ** 2
        current_iteration = 0

        # Build ranges
        lat_range = np.linspace(bb_s, bb_n, num=samples)
        lon_range = np.linspace(bb_w, bb_e, num=samples)

        # Build the array
        elements = []
        for lat_index in range(samples - 1):
            for lon_index in range(samples - 1):
                current_iteration += 1
                print 'Iteration %d/%d...' % (
                    current_iteration, total_iterations)

                # Get the values and build query
                query_bb_s = lat_range[lat_index]
                query_bb_n = lat_range[lat_index + 1]
                query_bb_w = lon_range[lon_index]
                query_bb_e = lon_range[lon_index + 1]
                ql_text = ql_template.format(
                    query_bb_s=query_bb_s, query_bb_w=query_bb_w,
                    query_bb_n=query_bb_n, query_bb_e=query_bb_e)

                # Safe to run multimple times, results are cached
                result = self.do_query(ql_text=ql_text)
                partial_elements = result.get('elements', [])
                print 'Partials elements found: %d' % len(partial_elements)
                elements += partial_elements

        # Done
        return elements
