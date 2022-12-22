import logging

from doi_pdf_mappers.abstract_doi_mapper import DoiMapper

logger = logging.getLogger(__name__)

class ScihubMapper(DoiMapper):
    """Get the PDF download URL for DOIs using Scihub."""
    def get_pdf_url(self, doi: str) -> str:
        url = f'https://sci.bban.top/pdf/{doi}.pdf#view=FitH'
        logger.debug(f'Built PDF URL {url}')
        return url