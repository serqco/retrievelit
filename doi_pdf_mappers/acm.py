import logging

from doi_pdf_mappers.abstract_mapper import Mapper

logger = logging.getLogger(__name__)

class AcmMapper(Mapper):
    def get_pdf_url(self, doi, resolved_doi):
        url = f'https://dl.acm.org/doi/pdf/{doi}'
        logger.debug(f'Built PDF URL {url}')
        return url