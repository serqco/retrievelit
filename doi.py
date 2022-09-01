import logging
import requests
import time
from tqdm import tqdm

import utils
from pipeline_step import PipelineStep

logger = logging.getLogger(__name__)

REQUEST_DELAY = 1

class DoiResolver(PipelineStep):
    def __init__(self, do_doi_rewrite):
        self._do_doi_rewrite = do_doi_rewrite
        self._metadata = []

    def _build_url(self, doi):
        return f'https://doi.org/{doi}'

    def _make_get_request(self, url):
        logger.debug(f'GET request to {url}')
        response = requests.get(url)
        logger.debug(f'Reponse code: {response.status_code}')
        response.raise_for_status()
        #TODO catch
        time.sleep(REQUEST_DELAY)
        return response

    def _rewrite_doi_url(self, response, doi):
        rewrite_url = 'ieeexplore.ieee.org'
        if rewrite_url not in response.url:
            return response
        new = f'https://doi.ieeecomputersociety.org/{doi}'
        logger.debug(f'Rewrote URL {response.url} to {new}')
        return self._make_get_request(new)

    def run(self):
        self._metadata = utils.load_metadata()
        for entry in tqdm(self._metadata):
            
            doi = entry.get('doi')
            if not doi:
                logger.warning(f'No DOI provided in entry {entry}. Skipping.')
                continue
            
            doi_url = self._build_url(doi)
            response = self._make_get_request(doi_url)
            
            if self._do_doi_rewrite:
                response = self._rewrite_doi_url(response, doi)
            
            resolved_doi = response.url
            logger.debug(f'Got resolved DOI {resolved_doi}')
            entry['resolved_doi'] = resolved_doi
        
        utils.save_metadata(self._metadata)