import logging

from doi_pdf_mappers.abstract_mapper import Mapper

logger = logging.getLogger(__name__)

class SpringerMapper(Mapper):
    def get_pdf_url(self, doi, resolved_doi):
        url = f'https://link.springer.com/content/pdf/{doi}.pdf'
        logger.debug(f'Built PDF URL {url}')
        return url