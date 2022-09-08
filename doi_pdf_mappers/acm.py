import logging

from doi_pdf_mappers.abstract_doi_mapper import DoiMapper

logger = logging.getLogger(__name__)

class AcmMapper(DoiMapper):
    def get_pdf_url(self, doi):
        url = f'https://dl.acm.org/doi/pdf/{doi}'
        logger.debug(f'Built PDF URL {url}')
        return url