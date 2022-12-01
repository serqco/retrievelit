import json
import logging
import typing as tg

logger = logging.getLogger(__name__)


def load_metadata(metadata_file: str) -> tg.List[tg.Dict]:
    """Load the metadata json into a python object and return it."""
    logger.debug(f'Loading metadata from file {metadata_file}')
    try:
        with open(metadata_file, 'r', encoding='utf8') as f:
            data = json.load(f)
    except OSError as e:
        logger.error(repr(e))
        logger.error('Error while loading metadata file.')
        raise SystemExit()
    logger.debug(f'Finished loading metadata from file {metadata_file}')
    return data


def save_metadata(metadata_file: str, data: tg.List[tg.Dict]) -> None:
    """Save the metadata into the metadata json file."""
    logger.debug(f'Saving metadata to file {metadata_file}')
    try:
        with open(metadata_file, 'w', encoding='utf8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    except OSError as e:
        logger.error(repr(e))
        logger.error('Error while saving metadata to file.')
        raise SystemExit()
    logger.debug(f'Finished writing metadata to file {metadata_file}') 