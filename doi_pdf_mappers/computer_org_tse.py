import logging

from doi_pdf_mappers.abstract_mapper import Mapper
from exceptions.doi_pdf_mappers import PdfUrlNotFoundError

logger = logging.getLogger(__name__)

class ComputerOrgTseMapper(Mapper):
    def get_pdf_url(self, doi, resolved_doi):
        ids = resolved_doi.split('/journal/')[1]
        if not ids:
            raise PdfUrlNotFoundError("Url doesn't match expected pattern.")
        url = f'https://www.computer.org/csdl/api/v1/periodical/trans/{ids}/download-article/pdf'
        logger.debug(f'Built PDF URL {url}')
        return url