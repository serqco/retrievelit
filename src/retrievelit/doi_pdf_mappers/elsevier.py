import logging

from retrievelit.doi_pdf_mappers.base import DoiMapper
from retrievelit.exceptions import PdfUrlNotFoundError

logger = logging.getLogger(__name__)

class ElsevierMapper(DoiMapper):
    """Get the PDF download URL for DOIs resolving to sciencedirect domains (Elsevier)."""
    def get_pdf_url(self, resolved_doi: str) -> str:
        logger.debug(f'get_pdf_url({resolved_doi})')
        ids = resolved_doi.split('/')[-1]
        if not ids:
            raise PdfUrlNotFoundError("Url doesn't match expected pattern.")
        url = f'https://www.sciencedirect.com/science/article/pii/{ids}/pdfft?isDTMRedir=true&download=true'
        logger.debug(f'Built PDF URL {url}')
        return url