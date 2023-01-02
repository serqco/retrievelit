import logging

from doi_pdf_mappers.abstract_doi_mapper import DoiMapper

logger = logging.getLogger(__name__)

class SpringerMapper(DoiMapper):
    """Get the PDF download URL for DOIs resolving to Springer domains."""
    def get_pdf_url(self, doi: str) -> str:
        url = f'https://link.springer.com/content/pdf/{doi}.pdf'
        logger.debug(f'Built PDF URL {url}')
        return url