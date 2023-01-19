import logging

from retrievelit.doi_pdf_mappers.base import DoiMapper, PDFDescriptor

logger = logging.getLogger(__name__)

class AcmMapper(DoiMapper):
    """Get the PDF download URL for DOIs resolving to ACM domains."""
    DL_LINK_BASE = "https://dl.acm.org/doi/pdf"

    def get_pdf_url(self, doi: str) -> str:
        url = f'{self.DL_LINK_BASE}/{doi}'
        logger.debug(f'Built PDF URL {url}')
        return url

    def get_pdfdescriptor(self, doi: str) -> PDFDescriptor:
        dl_link = self.get_pdf_url(doi)
        filename = "%s.pdf" % doi.split('/')[1]
        return PDFDescriptor(dl_link, filename)
