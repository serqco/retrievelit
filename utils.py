import json
import logging

logger = logging.getLogger(__name__)

#TODO add exceptions
def load_metadata(file):
    logger.debug(f'Loading metadata from file {file}')
    with open(file, 'r', encoding='utf8') as f:
        data = json.load(f)
    logger.debug(f'Finished loading metadata from file {file}')
    return data

def save_metadata(file, data):
    logger.debug(f'Saving metadata to file {file}')
    with open(file, 'w', encoding='utf8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    logger.debug(f'Finished writing metadata to file {file}') 