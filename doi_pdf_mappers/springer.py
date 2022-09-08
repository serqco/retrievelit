import logging

from doi_pdf_mappers.abstract_doi_mapper import DoiMapper

logger = logging.getLogger(__name__)

class SpringerMapper(DoiMapper):
    def get_pdf_url(self, doi):
        url = f'https://link.springer.com/content/pdf/{doi}.pdf'
        logger.debug(f'Built PDF URL {url}')
        return url