import logging
import json

logger = logging.getLogger(__name__)

METADATA_FILE = 'metadata.json'

#TODO add exceptions
def load_metadata():
    logger.debug(f'Loading metadata from file {METADATA_FILE}')
    with open(METADATA_FILE, 'r') as f:
        data = json.load(f)
    logger.debug(f'Finished loading metadata from file {METADATA_FILE}')
    return data

def save_metadata(data):
    logger.debug(f'Saving metadata to file {METADATA_FILE}')
    with open(METADATA_FILE, 'w') as f:
        f.write(json.dumps(data))
    logger.debug(f'Finished writing metadata to file {METADATA_FILE}') 