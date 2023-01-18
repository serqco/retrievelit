import logging

import requests

from retrievelit.doi_pdf_mappers.base import DoiMapper
from retrievelit.exceptions import PdfUrlNotFoundError

logger = logging.getLogger(__name__)


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


def _doi_ieeecs_url(doi: str) -> str:
    """Use this for resolving IEEE DOIs to computer.org instead of ieeeexplore.org."""
    return f"https://doi.ieeecomputersociety.org/{doi}"


class ComputerOrgConfMapper(DoiMapper):
    def get_pdf_url(self, the_doi):
        return _get_computer_org_pdf_url(
                the_doi,
                get_ids=lambda url: url.split('/')[-1],
                urlpattern='https://www.computer.org/csdl/pds/api/csdl/proceedings/download-article/%s/pdf'
        )


class ComputerOrgJournalMapper(DoiMapper):
    def get_pdf_url(self, the_doi):
        return _get_computer_org_pdf_url(
                the_doi,
                get_ids=lambda url: url.split('/journal/')[1],
                urlpattern='https://www.computer.org/csdl/api/v1/periodical/trans/%s/download-article/pdf'
        )
