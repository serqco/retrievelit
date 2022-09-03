import logging

from doi_pdf_mappers.abstract_mapper import Mapper
from exceptions.doi_pdf_mappers import PdfUrlNotFoundError

logger = logging.getLogger(__name__)

class ComputerOrgIcseMapper(Mapper):
    def get_pdf_url(self, doi, resolved_doi):
        ids = resolved_doi.split('/')[-1]
        if not ids:
            raise PdfUrlNotFoundError("Url doesn't match expected pattern.")
        url = f"https://www.computer.org/csdl/pds/api/csdl/proceedings/download-article/{ids}/pdf"
        logger.debug(f'Built PDF URL {url}')
        return url