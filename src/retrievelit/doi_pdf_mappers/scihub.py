import logging

from retrievelit.doi_pdf_mappers.abstract_doi_mapper import DoiMapper

logger = logging.getLogger(__name__)

SCIHUB_URL = 'https://sci.bban.top'  # changes frequently, one must correct it manually

class ScihubMapper(DoiMapper):
    """Get the PDF download URL for DOIs using Scihub."""
    def get_pdf_url(self, doi: str) -> str:
        url = f'{SCIHUB_URL}/pdf/{doi}.pdf#view=FitH'
        logger.debug(f'Built PDF URL {url}')
        return url