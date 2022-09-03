import logging
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
from tqdm import tqdm

import utils
from exceptions.doi_pdf_mappers import PdfUrlNotFoundError
from pipeline_step import PipelineStep

# seconds to wait between get requests (ignoring code execution time inbetween)
REQUEST_DELAY = 1

logger = logging.getLogger(__name__)

class PdfDownloader(PipelineStep):
    def __init__(self, doi_pdf_mapper, folder_name, list_file):
        self._mapper = doi_pdf_mapper
        self._folder_name = folder_name
        self._list_file = list_file
        self._metadata = []

    def _make_get_request(self, url):
        logger.debug(f'GET request to {url}')
        response = requests.get(url)
        logger.debug(f'Reponse code: {response.status_code}')
        response.raise_for_status()
        #TODO catch
        time.sleep(REQUEST_DELAY)
        return response

    def _store_pdf(self, pdf_data, filename):
        with open(filename, 'wb') as f:
            f.write(pdf_data)
        logger.debug(f'Wrote PDF to file {filename}')

    def _add_to_list(self, pdf_path):
        with open(self._list_file, 'a') as f:
            f.write(f'{pdf_path}\n')
        logger.debug(f'Added {pdf_path} to {self._list_file}.')

    def run(self):
        self._metadata = utils.load_metadata()
        # TODO implement more robust check
        # check if there's a failure to get the PDF URL multiple times in a row
        # which might point to no access.
        access_check_count = 0
        logger.info('Starting PDF download. This may take a few seconds per PDF.')
        for entry in tqdm(self._metadata):
            if access_check_count > 1:
                logger.error('Failed to get PDF URL too often - Aborting run. Please check if you have access to the publications, if you need to enable the --ieeecs flag, or if the the metadata-file is corrupted and try again.')
                raise SystemExit()

            if entry.get('pdf'):
                logger.debug(f'PDF already downloaded for entry {entry}. Skipping.')
                continue

            # TODO deduplicate
            resolved_doi = entry.get('resolved_doi')
            if not resolved_doi:
                logger.warning(f'No resolved DOI provided in entry {entry}. Skipping.')
                continue
            doi = entry.get('doi')
            if not doi:
                logger.warning(f'No DOI provided in entry {entry}. Skipping.')
                continue

            try:
                pdf_url = self._mapper.get_pdf_url(doi, resolved_doi)
            except PdfUrlNotFoundError as e:
                logger.warning(repr(e))
                logger.warning(f"No pdf URL found in URL {resolved_doi}. Skipping. If this reoccurs, check if you have access to this publication.")
                access_check_count += 1
                continue
            
            pdf_data = self._make_get_request(pdf_url).content
            filename = f"{self._folder_name}/{entry.get('identifier')}.pdf"
            if not filename:
                logger.warning(f'No identifier found in entry {entry}. Skipping.')
                continue
            self._store_pdf(pdf_data, filename)
            
            # this might lead to duplicate entries in the .list file
            # since it can get interrupted between appending to list file and saving the state
            # so we would append twice (can read in first and add to set if needed to combat this)
            #TODO should the path still contain the folder if the list file is in there aswell?
            self._add_to_list(filename)
            entry['pdf'] = True
            utils.save_metadata(self._metadata)

if __name__ == '__main__':
    # download_pdfs()
    logger.error('Not a standalone file. Please run the main script instead.')