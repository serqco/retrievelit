import json
import logging

logger = logging.getLogger(__name__)

#TODO add exceptions
def load_metadata(file):
    logger.debug(f'Loading metadata from file {file}')
    with open(file, 'r') as f:
        data = json.load(f)
    logger.debug(f'Finished loading metadata from file {file}')
    return data

def save_metadata(file, data):
    logger.debug(f'Saving metadata to file {file}')
    with open(file, 'w') as f:
        f.write(json.dumps(data))
    logger.debug(f'Finished writing metadata to file {file}') 