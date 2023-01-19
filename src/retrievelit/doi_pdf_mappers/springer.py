import logging

from retrievelit.doi_pdf_mappers.base import DoiMapper, PDFDescriptor

logger = logging.getLogger(__name__)

class SpringerMapper(DoiMapper):
    """Get the PDF download URL for DOIs resolving to Springer domains. As simple as it should be!"""
    DL_LINK_BASE = "https://link.springer.com/content/pdf"
    
    def get_pdf_url(self, doi: str) -> str:
        url = f'{self.DL_LINK_BASE}/{doi}.pdf'
        logger.debug(f'Built PDF URL {url}')
        return url

    def get_pdfdescriptor(self, doi: str) -> PDFDescriptor:
        dl_link = self.get_pdf_url(doi)
        filename = "%s.pdf" % (doi.split('/')[1])  # use second part of DOI
        return PDFDescriptor(dl_link, filename)