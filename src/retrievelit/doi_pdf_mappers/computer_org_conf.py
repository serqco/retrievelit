import logging

from retrievelit.doi_pdf_mappers.abstract_resolved_doi_mapper import ResolvedDoiMapper
from retrievelit.exceptions import PdfUrlNotFoundError

logger = logging.getLogger(__name__)

class ComputerOrgConfMapper(ResolvedDoiMapper):
    """Get the PDF download URL for DOIs resolving to conference publications on computer.org domains."""
    def get_pdf_url(self, resolved_doi: str) -> str:
        ids = resolved_doi.split('/')[-1]
        if not ids:
            raise PdfUrlNotFoundError("Url doesn't match expected pattern.")
        url = f"https://www.computer.org/csdl/pds/api/csdl/proceedings/download-article/{ids}/pdf"
        logger.debug(f'Built PDF URL {url}')
        return url