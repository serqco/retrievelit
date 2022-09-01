import logging
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
from tqdm import tqdm

import utils

# seconds to wait between get requests (ignoring code execution time inbetween)
REQUEST_DELAY = 1

logger = logging.getLogger(__name__)

def build_url(doi):
    return f'https://doi.org/{doi}'

def make_get_request(url):
    logger.debug(f'GET request to {url}')
    response = requests.get(url)
    logger.debug(f'Reponse code: {response.status_code}')
    response.raise_for_status()
    #TODO catch
    time.sleep(REQUEST_DELAY)
    return response

def rewrite_doi_url(response, doi):
    rewrite_url = 'ieeexplore.ieee.org'
    if rewrite_url not in response.url:
        return response
    new = f'https://doi.ieeecomputersociety.org/{doi}'
    logger.debug(f'Rewrote URL {response.url} to {new}')
    return make_get_request(new)

def get_pdf_url(response):
    # computer.org uses JS to populate website, so we need to get PDF URL from the URL itself
    response_url = response.url
    if 'computer.org' in response_url:
        # TODO try to make flexible for different venues
        # Transactions on Software Engineering (TSE)
        if 'journal/ts' in response_url:
            ids = response_url.split('/journal/')[1]
            #TODO this only works for TSE atm, since the venue isn't part of the original URL
            url = f'https://www.computer.org/csdl/api/v1/periodical/trans/{ids}/download-article/pdf'
        # International Conference on Software Engineering (ICSE)
        elif 'proceedings-article/icse' in response_url:
            ids = response_url.split('/')[-1]
            url = f"https://www.computer.org/csdl/pds/api/csdl/proceedings/download-article/{ids}/pdf"
        logger.debug(f'Built URL {url} for computer.org PDF download.')
        return url
    # for other URLs (Springer, ACM, etc.) parse HTML
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    #TODO make more robust (hardcode url schema somewhere for springer, etc. and lookup if it matches to prevent random URLs with 'pdf' from matching)
    element = soup.find('a', href=re.compile('[^A-z]pdf'))
    if not element:
        return None
    url = element.get('href')
    logger.debug(f'Extracted URL {url} for PDF download from HTML.')
    return url

def build_full_pdf_url(pdf_url, response_url):
    url = urljoin(response_url, pdf_url)
    logger.debug(f'Built full URL {url} for PDF download.')
    return url

def store_pdf(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)
    logger.debug(f'Wrote PDF to file {filename}')

def add_to_list(pdf_path, list_file):
    with open(list_file, 'a') as f:
        f.write(f'{pdf_path}\n')
    logger.debug(f'Added {pdf_path} to {list_file}.')

def download_pdfs(metadata_file, do_doi_rewrite, folder_name, list_file):
    entries = utils.load_metadata(metadata_file)
    # TODO implement more robust check
    # check if there's a failure to get the PDF URL multiple times in a row
    # which might point to no access.
    access_check_count = 0
    logger.info('Starting PDF download. This may take a few seconds per PDF.')
    #TODO fix progress bar if logger writes (https://stackoverflow.com/questions/38543506/change-logging-print-function-to-tqdm-write-so-logging-doesnt-interfere-wit)
    for entry in tqdm(entries):
        if access_check_count > 1:
            logger.error('Failed to get PDF URL too often - Aborting run. Please check if you have access to the publications, if you need to enable the --ieeecs flag, or if the the metadata-file is corrupted and try again.')
            sys.exit(1)

        if entry.get('pdf'):
            logger.debug(f'PDF already downloaded for entry {entry}. Skipping.')
            continue

        doi = entry.get('doi')
        if not doi:
            logger.warning(f'No DOI provided in entry {entry}. Skipping.')
            continue

        url = build_url(doi)
        response = make_get_request(url)
        if do_doi_rewrite:
            response = rewrite_doi_url(response, doi)

        pdf_url = get_pdf_url(response)
        if not pdf_url:
            logger.warning(f"No pdf URL found for DOI {doi}. Skipping. If this reoccurs, check if you have access to this publication.")
            access_check_count += 1
            continue
        # need this incase of relative URLs in href
        pdf_url = build_full_pdf_url(pdf_url, response.url)

        pdf = make_get_request(pdf_url).content
        filename = f"{folder_name}/{entry.get('identifier')}.pdf"
        if not filename:
            logger.warning(f'No identifier found in entry {entry}. Skipping.')
            continue
        store_pdf(pdf, filename)
        
        # this might lead to duplicate entries in the .list file
        # since it can get interrupted between appending to list file and saving the state
        # so we would append twice (can read in first and add to set if needed to combat this)
        add_to_list(filename, list_file)
        entry['pdf'] = True
        utils.save_metadata(metadata_file, entries)

if __name__ == '__main__':
    # download_pdfs()
    logger.error('Not a standalone file. Please run the main script instead.')