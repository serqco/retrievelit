import logging

from doi_pdf_mappers.abstract_mapper import Mapper

logger = logging.getLogger(__name__)

class ScihubMapper(Mapper):
    def get_pdf_url(self, doi, resolved_doi):
        url = f'https://sci.bban.top/pdf/{doi}.pdf#view=FitH'
        logger.debug(f'Built PDF URL {url}')
        return url