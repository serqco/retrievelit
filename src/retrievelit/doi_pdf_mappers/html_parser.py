from bs4 import BeautifulSoup
from retrievelit.doi_pdf_mappers.abstract_resolved_doi_mapper import ResolvedDoiMapper
from retrievelit.exceptions import PdfUrlNotFoundError
import logging
import time
import re
import requests

logger = logging.getLogger(__name__)

class HtmlParserMapper(ResolvedDoiMapper):
    """Get the PDF download URL from the content of a HTML page."""
    def __init__(self) -> None:
        self._html = ""
        
    def _get_html(self, url: str) -> None:
        """Get the HTML content for url."""
        logger.debug(f'GET request to {url}')
        response = requests.get(url)
        logger.debug(f'Reponse code: {response.status_code}')
        response.raise_for_status()
        self._html = response.text
        
    def get_pdf_url(self, resolved_doi: str) -> str:
        logger.debug('Getting PDF URL from site HTML.')
        time.sleep(1)
        self._get_html(resolved_doi)
        soup = BeautifulSoup(self._html, 'html.parser')
        element = soup.find('a', href=re.compile('[^A-z]pdf'))
        if not element:
            raise PdfUrlNotFoundError('Could not find PDF URL in site HTML.')
        url = element.get('href')
        logger.debug(f'Found PDF URL {url}')
        return url