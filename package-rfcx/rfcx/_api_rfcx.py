import httplib2
import json
import logging
from six.moves import http_client
from six.moves import urllib

logger = logging.getLogger(__name__)

host = 'https://api.rfcx.org'  # TODO move to configuration

def tags(token, type, labels, start, end, sites, limit):
    data = {'type': type, 'values[]': labels, 'starting_after_local': start, 'starting_before_local': end, 'sites[]': sites, 'limit': limit}
    path = '/v2/tags'
    url = '{}{}?{}'.format(host, path, urllib.parse.urlencode(data, True))
    return _request(url, token=token)

def streamSegments(token, stream_id, start, end, limit, offset):
    data = {'id': stream_id, 'start': start, 'end': end, 'limit': limit, 'offset': offset}
    path = f'/streams/{stream_id}/stream-segments'
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
