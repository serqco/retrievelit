import logging
import requests
import time
import typing as tg
from tqdm import tqdm

import utils
from pipeline_step import PipelineStep

logger = logging.getLogger(__name__)

REQUEST_DELAY = 1

class DoiResolver(PipelineStep):
    """Resolve the DOI by sending a GET request to the DOI and following all redirects."""
    def __init__(self, metadata_file: str, do_doi_rewrite: bool) -> None:
        self._metadata_file = metadata_file
        self._do_doi_rewrite = do_doi_rewrite
        self._metadata: tg.List = []

    def _build_url(self, doi: str) -> str:
        """Return the DOI URL to resolve the given DOI."""
        return f'https://doi.org/{doi}'

    def _rewrite_doi_url(self, response: requests.Response, doi: str) -> requests.Response:
        """Rewrite the DOI URL if it resolved to a IEEE domain. 
        
        Make a GET request to the new URL and return the response if it did.
        Otherwise return the original response.
        """
        rewrite_url = 'ieeexplore.ieee.org'
        if rewrite_url not in response.url:
            return response
        new = f'https://doi.ieeecomputersociety.org/{doi}'
        logger.debug(f'Rewrote URL {response.url} to {new}')
        return utils.make_get_request(new, REQUEST_DELAY)

    def run(self) -> None:
        """Run the full resolve process."""
        self._metadata = utils.load_metadata(self._metadata_file)
        for entry in tqdm(self._metadata):
            
            doi = entry.get('doi')
            if not doi:
                logger.warning(f'No DOI provided in entry {entry}. Skipping.')
                continue
            
            doi_url = self._build_url(doi)
            response = utils.make_get_request(doi_url, REQUEST_DELAY)
            
            if self._do_doi_rewrite:
                response = self._rewrite_doi_url(response, doi)
            
            resolved_doi = response.url
            logger.debug(f'Got resolved DOI {resolved_doi}')
            entry['resolved_doi'] = resolved_doi
        utils.save_metadata(self._metadata_file, self._metadata)
