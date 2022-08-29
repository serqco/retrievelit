from bs4 import BeautifulSoup
import requests
import re
import json
import logging
import sys

import utils

logger = logging.getLogger(__name__)

BASE_URL = 'https://dblp.org/db/'
API_BASE_URL = 'https://dblp.org/search/publ/api?q=toc:db/'

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

def is_conference(venue):
    return venue['type'] == 'conference'

def is_journal(venue):
    return venue['type'] == 'journal'

def build_venue_url(dblp_config):
    url = f"{BASE_URL}{dblp_config['type']}/{dblp_config['acronym']}"
    logger.debug(f'Built URL: {url}')
    return url

def get_volume_number(venue_url, year):
    """
    
    """
    #TODO multiple volumes for one year?
    logger.debug('Searching for volume number.')
    logger.debug(f'Venue url: {venue_url}')
    logger.debug(f'Year: {year}')
    r = requests.get(venue_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # find "Volume" and "2021" in <a> tag
    tag = soup.find('a', string=re.compile(f'Volume.*{year}'))
    logger.debug(f'Volume number html tag: {tag}')
    # print(tag.text)
    volume_number = tag.text.split('Volume ')[1].split(',')[0]
    logger.debug(f'Extracted volume number {volume_number}')
    return volume_number

def build_volume_url(dblp_config, volume_number):
    """

    """
    venue_type = dblp_config['type']
    acronym = dblp_config['acronym']
    result_number = 1000
    result_format = 'json'
    url = f"{API_BASE_URL}{venue_type}/{acronym}/{acronym}{volume_number}.bht:&h={result_number}&format={result_format}"
    logger.debug(f'Built volume url: {url}')
    return url

def get_volume_data(url):
    """
    
    """
    r = requests.get(url)
    return r.json()

def unify_data_format(data):
    """
    
    """
    result = []
    for publication in data['result']['hits']['hit']:
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


def download_metadata(venue, year, metadata_file):
    logger.info(f'Downloading metadata.')
    logger.debug(f'venue: {venue}')
    logger.debug(f'year: {year}')
    veryify_mds_config(venue)
    # mds = metadata-source
    mds_config = load_mds_config(venue)
    if is_conference(venue):
        volume_number = year
    elif is_journal(venue):
        # TODO make sure this exists, probably check for all
        # fields in loading function, once determined which are needed
        venue_url = build_venue_url(mds_config)
        volume_number = get_volume_number(venue_url, year)
    else:
        logger.error(f"Couldn't determine type of venue {venue}. Review venues.py file and try again.")
        sys.exit(1)
    volume_url = build_volume_url(mds_config, volume_number)
    data = get_volume_data(volume_url)
    logger.info('Metadata received.')
    logger.info('Rewriting data in uniform format.')
    unified_data = unify_data_format(data)
    utils.save_metadata(metadata_file, unified_data)

if __name__ == '__main__':
    # TODO function that adds the venue type in url format to the object
    # download_metadata(venue, '2021')
    logger.error('Not a standalone file. Please run the main script instead.')
