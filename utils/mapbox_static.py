'''
See this for some meta info about the basemap:
http://api.tiles.mapbox.com/v4/${MAPBOX_MAPID}.json?access_token=${MAPBOX_ACCESS_TOKEN}
'''

import os
import urllib

# Base URL
MAPBOX_ENDPOINT = (
    'http://api.tiles.mapbox.com/v4/{mapid}/{lon},{lat},{zoom}'
    '/{width}x{height}.{format}?access_token={access_token}')

# Params
MAPBOX_MAPID = 'zugaldia.mfecmd32'
MAPBOX_ACCESS_TOKEN = os.environ["mapbox_token"]
MAPBOX_FORMAT = 'png'
MAPBOX_WIDTH = '1280'
MAPBOX_HEIGHT = '1280'
MAPBOX_ZOOM = 19  # Max zoom


class MapboxStatic(object):

    def __init__(self, namespace=None, root_folder=None):
        self._namespace = namespace or 'mapbox'
        self._root_folder = root_folder or '/tmp'
        if not os.path.isdir(self._root_folder):
            try:
                os.mkdir(self._root_folder)
                print '[mapbox static] Root folder created: %s' \
                    % self._root_folder
            except Exception as e:
                print '[mapbox static] Failed to create the root folder \
                    (%s): %s' % (self._root_folder, unicode(e))

    def _get_filepath(self, element_id):
        filename = '%s_%s.%s' % (self._namespace, element_id, MAPBOX_FORMAT)
        return os.path.join(self._root_folder, filename)

    def _get_filesize(self, filepath):
        statinfo = os.stat(filepath)
        return statinfo.st_size

    def get_url(self, latitude, longitude):
        return MAPBOX_ENDPOINT.format(
            mapid=MAPBOX_MAPID,
            lon=longitude,
            lat=latitude,
            zoom=MAPBOX_ZOOM,
            width=MAPBOX_WIDTH,
            height=MAPBOX_HEIGHT,
            format=MAPBOX_FORMAT,
            access_token=MAPBOX_ACCESS_TOKEN)

    def download_tile(self, element_id, url):
        filepath = self._get_filepath(element_id=element_id)
        if os.path.isfile(filepath):
            print '[mapbox static] Tile already downloaded (%s).' % filepath
            return
        print '[mapbox static] Donwloading tile (%s).' % filepath
        urllib.urlretrieve(url=url, filename=filepath)

        # Detect if we have actual imagery here
        filesize = self._get_filesize(filepath=filepath)
        if filesize < 50000:
            print 'Deleting downloaded file, it looks like an empty image.'
            os.remove(filepath)
            return False
        return True
