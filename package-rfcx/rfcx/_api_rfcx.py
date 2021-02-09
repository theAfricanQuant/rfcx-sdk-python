import httplib2
import json
import logging
from six.moves import http_client
from six.moves import urllib

logger = logging.getLogger(__name__)

host = 'https://api.rfcx.org'  # TODO move to configuration

def streamSegments(token, stream_id, start, end, limit, offset):
    data = {'id': stream_id, 'start': start, 'end': end, 'limit': limit, 'offset': offset}
    path = f'/streams/{stream_id}/stream-segments'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)

def annotations(token, start, end, classifications=None, stream=None, limit=1000, offset=0):
    data = {'start': start, 'end': end, 'classifications[]': classifications, 'stream_id': stream, 'limit': limit, 'offset': offset}
    path = '/annotations'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)

# TODO: Add the organizations/projects when the API support
def streams(token, keyword=None, limit=1000, offset=0):
    data = {'keyword': keyword, 'limit': limit, 'offset': offset}
    path = '/streams'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)

def _request(url, method='GET', token=None):
    logger.debug('get url: ' + url)

    if token != None:
        headers = {'Authorization': 'Bearer ' + token}
    else:
        headers = {}

    http = httplib2.Http()
    resp, content = http.request(url, method=method, headers=headers)

    if resp.status == http_client.OK:
        return json.loads(content)
    
    logger.error(f'HTTP status: {resp.status}')

    return None
