import json
import logging
import typing as tg
import time
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


def load_metadata(metadata_file: Path) -> tg.List[tg.Dict]:
    """Load the corpus metadata from the metadata file and return it."""
    logger.debug(f'Loading metadata from file {metadata_file}')
    try:
        with open(metadata_file, 'r', encoding='utf8') as f:
            file_content = json.load(f)
    except OSError as e:
        logger.error(repr(e))
        logger.error('Error while loading metadata file.')
        raise SystemExit()
    try:
        metadata = file_content['corpus_metadata']
    except KeyError:
        logger.error(f"Metadata file {metadata_file} does not contain corpus metadata.")
        raise SystemExit()
    logger.debug(f'Finished loading metadata from file {metadata_file}')
    return metadata


def save_metadata(metadata_file: Path, data: tg.List[tg.Dict]) -> None:
    """Save the corpus metadata to the metadata file."""
    logger.debug(f'Saving corpus metadata to file {metadata_file}')
    try:
        with open(metadata_file, 'r', encoding='utf8') as f:
            file_content = json.load(f)
        file_content['corpus_metadata'] = data
        with open(metadata_file, 'w', encoding='utf8') as f:
            f.write(json.dumps(file_content, ensure_ascii=False, indent=2, sort_keys=True))
    except OSError as e:
        logger.error(repr(e))
        logger.error('Error while saving corpus metadata to file.')
        raise SystemExit()
    logger.debug(f'Finished writing corpus metadata to file {metadata_file}') 

def make_get_request(url: str, delay: int = 0) -> requests.Response:
    """Make a GET request to url and return the response if successful."""
    time.sleep(delay)
    logger.debug(f'GET request to {url}')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'}
    response = requests.get(url, headers=headers)
    logger.debug(f'Reponse code: {response.status_code}')
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        logger.error(f'Bad Reponse from GET requests. {e}')
        raise SystemExit() 
    return response