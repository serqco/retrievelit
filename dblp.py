from bs4 import BeautifulSoup
from pprint import pprint
import requests
import re
import json
import logging

import utils

logger = logging.getLogger(__name__)

BASE_URL = 'https://dblp.org/db/'

# EXAMPLE_TOKEN = "toc:db/journals/ese/ese26.bht:"

def build_venue_url(venue):
    """
    
    """
    url = f"{BASE_URL}{venue['type_url']}/{venue['acronym']}"
    logger.debug(f'Built URL: {url}')
    return url

# query venue api for specific venue
#TODO finish
def find_venue(venue):
    """
    
    """
    
    API_URL = 'https://dblp.org/search/venue/api'

    name_query_string = '+'.join(venue.get('name').split())
    url_params = {
        'format': 'json',
        'q': name_query_string,
    }
    r = requests.get(API_URL, params=url_params)
    print(r.text)

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

def build_volume_url(venue, volume_number):
    """

    """
    venue_type = venue['type_url']
    acronym = venue['acronym']
    result_number = 1000
    result_format = 'json'
    url = f"https://dblp.org/search/publ/api?q=toc:db/{venue_type}/{acronym}/{acronym}{volume_number}.bht:&h={result_number}&format={result_format}"
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
        entry = {key: publication[key] for key in keys}
        
        # create list of author names
        authors = publication.get('authors')
        if not authors:
            #TODO LOGGING WARNING
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
        
        entry['bibtext'] = False
        entry['pdf'] = False

        logger.debug(f'created entry: {entry}')
        result.append(entry)
    return result


# r = requests.get("https://dblp.org/db/journals/ese/ese26.html")

def download_metadata(venue, year, metadata_file):
    logger.info(f'Downloading metadata.')
    logger.debug(f'venue: {venue}')
    logger.debug(f'year: {year}')
    venue_url = build_venue_url(venue)
    volume_number = get_volume_number(venue_url, year)
    volume_url = build_volume_url(venue, volume_number)
    data = get_volume_data(volume_url)
    logger.info('Metadata received.')
    logger.info('Rewriting data in uniform format.')
    unified_data = unify_data_format(data)
    utils.save_metadata(metadata_file, unified_data)

if __name__ == '__main__':
    # type can be journal or conference
    venue = {
        'name': 'empirical software engineering',
        'acronym': 'ese',
        'type': 'journal',
        'type_url': 'journals',
    }
    # TODO function that adds the venue type in url format to the object
    download_metadata(venue, '2021')
