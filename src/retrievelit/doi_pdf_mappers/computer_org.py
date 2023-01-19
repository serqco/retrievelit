import logging

import requests

from retrievelit.doi_pdf_mappers.base import DoiMapper, PDFDescriptor
from retrievelit.exceptions import PdfUrlNotFoundError

logger = logging.getLogger(__name__)

"""
IEEE Computer Society Digital Library:

Conferences (as of 2023-01-19):

DOIs such as 10.1109/EnCyCriS52570.2021.00009 resolve to a URL of the form
https://www.computer.org/csdl/proceedings-article/encycris/2021/455300a009/1v5664WCYUg
which is a webpage containing a download link of the form
https://www.computer.org/csdl/pds/api/csdl/proceedings/download-article/1v5664WCYUg/pdf
which leads to a download filename of the form
455300a009.pdf.
So we need the last component of the DOI target for the download link ('linkpart')
and the next-to-last component for the PDF filename ('namepart').

Journals (as of 2023-01-19):

DOIs such as 10.1109/TSE.2022.3152148 resolve to a URL of the form
https://www.computer.org/csdl/journal/ts/2023/01/09714872/1B2DgCfp7gs
which is a webpage containing a download link of the form
https://www.computer.org/csdl/api/v1/periodical/trans/ts/2023/01/09714872/1B2DgCfp7gs/download-article/pdf
which leads to a download filename of the form
09714872.pdf.
So we need the last 5 components of the DOI target (all after /journal/) for the download link
and the next-to-last component for the PDF filename.
"""

def _get_computer_org_pdf_url(the_doi: str, get_ids: callable, urlpattern: str) -> str:
    logger.debug(f'get_pdf_url({the_doi})')
    response = requests.head(_doi_ieeecs_url(the_doi), allow_redirects=True)
    resolved_url = response.url
    logger.debug(f'---> {resolved_url}')
    ids = get_ids(resolved_url)
    if not ids:
        raise PdfUrlNotFoundError(f"Url '{resolved_url}' doesn't match expected pattern.")
    url = urlpattern % ids
    logger.debug(f'---> {url}')
    return url


def _get_pdfdescriptor(the_doi: str, get_ids: callable, urlpattern: str) -> PDFDescriptor:
    resolved_url = _get_resolved_url(the_doi)
    ids = get_ids(resolved_url)
    if not ids:
        raise PdfUrlNotFoundError(f"Url '{resolved_url}' doesn't match expected pattern.")
    url = urlpattern % ids
    logger.debug(f'---> {url}')
    return url


def _get_resolved_url(doi: str) -> str:
    logger.debug(f'get_pdf_url({doi})')
    response = requests.head(_doi_ieeecs_url(doi), allow_redirects=True)
    resolved_url = response.url
    logger.debug(f'---> {resolved_url}')
    return resolved_url


def _doi_ieeecs_url(doi: str) -> str:
    """Use this for resolving IEEE DOIs to computer.org instead of ieeeexplore.org."""
    return f"https://doi.ieeecomputersociety.org/{doi}"


class ComputerOrgConfMapper(DoiMapper):
    DL_LINK_BASE = "https://www.computer.org/csdl/pds/api/csdl/proceedings/download-article"

    def get_pdf_url(self, the_doi):
        return _get_computer_org_pdf_url(
            the_doi,
            get_ids=lambda url: url.split('/')[-1],
            urlpattern='https://www.computer.org/csdl/pds/api/csdl/proceedings/download-article/%s/pdf'
        )

    def get_pdfdescriptor(self, the_doi: str) -> PDFDescriptor:
        resolved_url = _get_resolved_url(the_doi)
        two_ids = resolved_url.split('/')[-2:]  # the two last path elements
        dl_link = f"{self.DL_LINK_BASE}/{two_ids[1]}/pdf"
        filename = f"{two_ids[0]}.pdf"
        return PDFDescriptor(dl_link, filename)


class ComputerOrgJournalMapper(DoiMapper):
    DL_LINK_BASE = "https://www.computer.org/csdl/api/v1/periodical/trans"
    def get_pdf_url(self, the_doi):
        return _get_pdfdescriptor(
                the_doi,
                get_ids=lambda url: url.split('/journal/')[1],
                urlpattern='https://www.computer.org/csdl/api/v1/periodical/trans/%s/download-article/pdf'
        )

    def get_pdfdescriptor(self, the_doi: str) -> PDFDescriptor:
        resolved_url = _get_resolved_url(the_doi)
        several_ids_part = resolved_url.split('/journal/')[1]  # several path elements
        dl_link = f"{self.DL_LINK_BASE}/{several_ids_part}/download-article/pdf"
        several_ids = several_ids_part.split('/')
        filename = f"{several_ids[-2]}.pdf"
        return PDFDescriptor(dl_link, filename)
