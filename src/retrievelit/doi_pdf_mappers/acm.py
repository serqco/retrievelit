import logging

from retrievelit.doi_pdf_mappers.base import DoiMapper

logger = logging.getLogger(__name__)

class AcmMapper(DoiMapper):
    """Get the PDF download URL for DOIs resolving to ACM domains."""
    def get_pdf_url(self, doi: str) -> str:
        url = f'https://dl.acm.org/doi/pdf/{doi}'
        logger.debug(f'Built PDF URL {url}')
        return url