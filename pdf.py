from fileinput import filename
from bs4 import BeautifulSoup
import tqdm
# from tqdm.contrib.logging import logging_redirect_tqdm
import logging
import requests
import re
import time

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

def get_pdf_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    element = soup.find('a', href=re.compile('pdf'))
    url = element.get('href')
    logger.debug(f'Extracted URL {url} for pdf download.')
    return url

def store_pdf(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)
    logger.debug(f'Wrote PDF to file {filename}')

def download_pdfs(metadata_file, do_doi_rewrite, folder_name):
    # open metadata file
    entries = utils.load_metadata(metadata_file)
    # iterate over entries
    with tqdm.contrib.logging.logging_redirect_tqdm():
        for entry in tqdm(entries):
            if entry.get('pdf'):
                continue
            doi = entry.get('doi')
            if not doi:
                logger.warning(f'No DOI provided in entry {entry}. Skipping.')
                continue
            url = build_url(doi)
            response = make_get_request(url)
            if do_doi_rewrite:
                response = rewrite_doi_url(response, doi)
            pdf_url = get_pdf_url(response.text)
            if not pdf_url:
                logger.warning(f"No pdf URL found for DOI {doi}. Skipping.")
                continue
            pdf = make_get_request(pdf_url).content
            filename = f"{folder_name}/{entry.get('identifier')}.pdf"
            if not filename:
                logger.warning(f'No identifier found in entry {entry}. Skipping.')
                continue
            store_pdf(pdf)
            entry['pdf'] = True
            utils.save_metadata(metadata_file, entries)

    # add local path to list file


if __name__ == '__main__':
    download_pdfs()