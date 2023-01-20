import logging
import pydoi

from retrievelit.doi_pdf_mappers.base import DoiMapper, PDFDescriptor
from retrievelit.exceptions import PdfUrlNotFoundError

logger = logging.getLogger(__name__)

class ElsevierMapper(DoiMapper):
    """Get the PDF download URL for DOIs resolving to sciencedirect domains (Elsevier)."""
    DL_LINK_BASE = "https://www.sciencedirect.com/science/article/pii"

    def get_pdf_url(self, doi: str) -> str:
        logger.debug(f'get_pdf_url({doi})')
        elsevier_id = pydoi.get_url(doi).split('/')[-1]
        if not elsevier_id:
            raise PdfUrlNotFoundError("Url doesn't match expected pattern.")
        url = f'{self.DL_LINK_BASE}/{elsevier_id}/pdfft?isDTMRedir=true&download=true'
        logger.debug(f'Built PDF URL {url}')
        return url

    def get_pdfdescriptor(self, doi: str) -> PDFDescriptor:
        pdf_dl_url = self.get_pdf_url(doi)
        elsevier_id = pydoi.get_url(doi).split('/')[-1]
        download_filename = f'1-s2.0-{elsevier_id}-main.pdf'
        return PDFDescriptor(pdf_dl_url, download_filename)
