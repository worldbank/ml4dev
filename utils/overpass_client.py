from restwice import RestClient
from restwice import MemcacheLocal

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

    def query(self, ql_text=None):
        data = self._get_data(ql_text=ql_text)
        self._rest_client.set_data(data={'data': data})
        result, _ = self._rest_client.do_get(
            json_response=True,
            json_request=False,
            client_settings=self._client_settings)
        return result
