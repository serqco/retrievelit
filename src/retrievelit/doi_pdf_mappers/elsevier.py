import logging

import requests

from retrievelit.doi_pdf_mappers.base import DoiMapper, PDFDescriptor
from retrievelit.exceptions import PdfUrlNotFoundError

logger = logging.getLogger(__name__)

class ElsevierMapper(DoiMapper):
    """Get the PDF download URL for DOIs resolving to sciencedirect domains (Elsevier)."""
    DL_LINK_BASE = "https://www.sciencedirect.com/science/article/pii"

    def _elsevier_id_from_doi(self, doi):
        response = requests.head(f'https://doi.org/{doi}', allow_redirects=True)
        resolved_url = response.url
        elsevier_id = resolved_url.split('/')[-1]
        return elsevier_id

    def get_pdf_url(self, doi: str) -> str:
        logger.debug(f'get_pdf_url({doi})')
        elsevier_id = self._elsevier_id_from_doi(doi)
        if not elsevier_id:
            raise PdfUrlNotFoundError("Url doesn't match expected pattern.")
        url = f'{self.DL_LINK_BASE}/{elsevier_id}/pdfft?isDTMRedir=true&download=true'
        logger.debug(f'Built PDF URL {url}')
        return url

    def get_pdfdescriptor(self, doi: str) -> PDFDescriptor:
        pdf_dl_url = self.get_pdf_url(doi)
        elsevier_id = self._elsevier_id_from_doi(doi)
        download_filename = f'1-s2.0-{elsevier_id}-main.pdf'
        return PDFDescriptor(pdf_dl_url, download_filename)
