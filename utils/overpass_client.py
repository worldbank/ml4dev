from restwice import RestClient
from restwice import MemcacheLocal

ENDPOINT = 'http://overpass-api.de/api/interpreter'
MEMCACHE_NAMESPACE = 'overpass'


class OverpassClient(object):
    def __init__(self):
        self._rest_client = RestClient()
        self._rest_client.set_endpoint(endpoint=ENDPOINT)

        # Set local caching
        memcache_client = MemcacheLocal(root_folder='_cache_overpass')
        self._rest_client.enable_cache(
            memcache_client=memcache_client,
            memcache_namespace=MEMCACHE_NAMESPACE)

    def _get_data(self, ql_text):
        entries = []
        entries.append('[out:json]')
        if ql_text:
            entries.append(ql_text)
        entries.append('out;')
        return ';'.join(entries)

    def query(self, ql_text=None):
        data = self._get_data(ql_text=ql_text)
        self._rest_client.set_data(data={'data': data})
        result, _ = self._rest_client.do_get(
            json_response=True,
            json_request=False)
        return result
