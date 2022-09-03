import json
import logging

logger = logging.getLogger(__name__)

METADATA_FILE = 'metadata.json'

def load_metadata():
    logger.debug(f'Loading metadata from file {METADATA_FILE}')
    try:
        with open(METADATA_FILE, 'r', encoding='utf8') as f:
            data = json.load(f)
    except OSError as e:
        logger.error(repr(e))
        logger.error('Error while loading metadata file.')
        raise SystemExit()
    logger.debug(f'Finished loading metadata from file {METADATA_FILE}')
    return data

def save_metadata(data):
    logger.debug(f'Saving metadata to file {METADATA_FILE}')
    try:
        with open(METADATA_FILE, 'w', encoding='utf8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    except OSError as e:
        logger.error(repr(e))
        logger.error('Error while saving metadata to file.')
        raise SystemExit()
    logger.debug(f'Finished writing metadata to file {METADATA_FILE}') 