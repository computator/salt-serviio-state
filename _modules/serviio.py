import requests
import logging
log = logging.getLogger(__name__)

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 23423

SHARED_FOLDER_TPL = {
    'folderPath': '',
    'supportedFileTypes': ['IMAGE'],
    'descriptiveMetadataSupported': True,
    'accessGroupIds': [1],
    'usePoller': False
}

def _api_get(method, host=DEFAULT_HOST, port=DEFAULT_PORT, **kwargs):
    url = 'http://{0}:{1}/rest/{2}'.format(host, port, method)
    log.info("Calling URL '%s'", url)
    resp = requests.get(url, headers={'Accept': 'application/json'}, timeout=10)
    log.info("Response data: '%s'", resp.text)
    resp.raise_for_status()
    return resp.json()

def _api_set(method, data, host=DEFAULT_HOST, port=DEFAULT_PORT, **kwargs):
    url = 'http://{0}:{1}/rest/{2}'.format(host, port, method)
    log.info("Calling URL '%s' with data: %s", url, data)
    resp = requests.put(url, json=data, headers={'Accept': 'application/json'}, timeout=10)
    if not resp.ok:
        log.warning("Recieved bad response from '%s': '%s'", url, resp.text)
    else:
        log.info("Response data: '%s'", resp.text)
    resp.raise_for_status()
    return resp.json()

def get_library(**kwargs):
    return _api_get('repository', **kwargs)['sharedFolders']

def set_library(library, **kwargs):
    library = map(lambda folder: dict(SHARED_FOLDER_TPL, **folder), library)
    return _api_set('repository', {'sharedFolders': library}, **kwargs)

def update_library(library, test=False, **kwargs):
    library = map(lambda folder: dict(SHARED_FOLDER_TPL, **folder), library)
    old_data = get_library(**kwargs)
    tmp_data = {folder['folderPath']: folder.copy() for folder in old_data}
    new_data = []
    for folder in library:
        if folder['folderPath'] in tmp_data:
            tmp_data[folder['folderPath']].update(folder)
            folder = tmp_data[folder['folderPath']]
            del tmp_data[folder['folderPath']]
        new_data.append(folder)
    if test:
        log.trace("Old: %s", old_data)
        log.trace("New: %s", new_data)
        return old_data != new_data
    return set_library(new_data, **kwargs)