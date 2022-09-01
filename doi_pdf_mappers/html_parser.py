from bs4 import BeautifulSoup
from doi_pdf_mappers.abstract_mapper import Mapper
from exceptions.doi_pdf_mappers import PdfUrlNotFoundError
import logging
import time
import re
import requests

logger = logging.getLogger(__name__)

class HtmlParserMapper(Mapper):
    def __init__(self):
        self._html = ""
        
    def _get_html(self, url):
        logger.debug(f'GET request to {url}')
        response = requests.get(url)
        logger.debug(f'Reponse code: {response.status_code}')
        response.raise_for_status()
        self._html = response.text
        
    def get_pdf_url(self, doi, resolved_doi):
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