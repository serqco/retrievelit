import requests
import re
import json
import logging
import sys
import time

import utils

logger = logging.getLogger(__name__)

BASE_URL = 'https://dblp.org/db/'
API_BASE_URL = 'https://dblp.org/search/publ/api?q='

# EXAMPLE_TOKEN = "toc:db/journals/ese/ese26.bht:"

# mds = metadata-source
def veryify_mds_config(venue):
    try:
        mds_config = venue['metadata_sources']['dblp']
        venue_type = mds_config['type']
        acronym = mds_config['acronym']
        if not venue_type: raise ValueError('\'type\'')
        if not acronym: raise ValueError('\'acronym\'')
    except (KeyError, ValueError) as e:
        logger.error(f"Value missing from venues.py: {str(e)}. Please make sure the configuration adheres to the expected format, or try another metadata-source.")
        sys.exit(1)

def load_mds_config(venue):
    metadata_config = venue['metadata_sources']['dblp']
    return metadata_config



def get_data_for_year(mds_config, year):
    url = 'https://dblp.org/search/publ/api?q=stream:streams/journals/ese:&h=1000&format=json'
    venue_type = mds_config['type']
    acronym = mds_config['acronym']
    offset = 0
    received = 0
    entries = []
    while True:
        url = f"{API_BASE_URL}stream:streams/{venue_type}/{acronym}:&h=1000&f={offset}&format=json"
        data = get_data(url)
        hits = data['result']['hits']
        received += int(hits['@sent'])
        total = int(hits['@total'])
        logger.debug(f"Received {received} entries. Amount in collection: {total}.")
        entries.extend(hits['hit'])
        if received >= total:
            logger.debug(f"Received all entries.")
            break
        logger.debug(f"{total - received} entries left. Getting next batch.")
        offset += 1000
        time.sleep(1)
        
    logger.debug(f"{len(entries)} entries received from publ API.")
    logger.debug("Filtering out entries from other years.")
    year_entries = [e for e in entries if e['info']['year'] == year]
    logger.debug(f"{len(year_entries)} entries found for year {year}.")
    return year_entries
    
def build_volume_url(mds_config, volume_number):
    venue_type = mds_config['type']
    acronym = mds_config['acronym']
    url = f"{API_BASE_URL}toc:db/{venue_type}/{acronym}/{acronym}{volume_number}.bht:&h=1000&format=json"
    logger.debug(f'Built volume url: {url}')
    return url

def get_data(url):
    logger.debug(f'GET request to {url}')
    r = requests.get(url)
    logger.debug(f'Reponse code: {r.status_code}')
    r.raise_for_status()
    return r.json()

def get_data_for_volume(mds_config, volume):
    volume_url = build_volume_url(mds_config, volume)
    data = get_data(volume_url)
    entries = data['result']['hits']['hit']
    logger.debug(f"Received {len(entries)} entries for volume {volume}.")
    return entries

def unify_data_format(hits):
    """
    
    """
    result = []
    for publication in hits:
        publication = publication['info']

        keys = ['title', 'venue', 'volume', 'number', 'year', 'doi']
        #TODO if venue name is different for each metadata source, this needs to come from venues.py
        # only journals have volume and number fields
        entry = {key: publication.get(key) for key in keys}
        
        # create list of author names
        authors = publication.get('authors')
        if not authors:
            logger.warning(f"Dropped entry without author: {publication}")
            continue

        author = authors['author']
        # dblp author value sometimes contains numbers at the end (e. g. "Max Mueller 001")
        # so strip numbers and whitespace
        strip_values = "0123456789" + " "
        # field 'author' can be a single value or a list in the json returned from dblp
        if isinstance(author, list):
            entry['authors'] = [e['text'].strip(strip_values) for e in author]
        elif isinstance(author, dict):
            # create list with 1 element here to get rid of this check in the next steps
            entry['authors'] = [author['text'].strip(strip_values)]
        entry['pdf'] = False

        logger.debug(f'created entry: {entry}')
        result.append(entry)
    return result


def download_metadata(venue, number, grouping, metadata_file):
    logger.info(f'Downloading metadata.')
    logger.debug(f'venue: {venue}')
    logger.debug(f'year or volume: {number}')
    logger.debug(f'grouping: {grouping}')
    
    veryify_mds_config(venue)
    # mds = metadata-source
    mds_config = load_mds_config(venue)
    if grouping == 'year':
        data = get_data_for_year(mds_config, number)
    if grouping == 'volume':
        data = get_data_for_volume(mds_config, number)

    logger.info('Metadata received.')
    logger.info('Rewriting data in uniform format.')
    unified_data = unify_data_format(data)
    utils.save_metadata(metadata_file, unified_data)

if __name__ == '__main__':
    # download_metadata(venue, '2021')
    logger.error('Not a standalone file. Please run the main script instead.')
