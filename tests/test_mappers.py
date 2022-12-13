import requests
import pytest

from doi_pdf_mappers.acm import AcmMapper
from doi_pdf_mappers.computer_org_conf import ComputerOrgConfMapper
from doi_pdf_mappers.computer_org_journal import ComputerOrgJournalMapper
# from doi_pdf_mappers.html_parser import HtmlParserMapper
from doi_pdf_mappers.springer import SpringerMapper

inputs = [
    (AcmMapper, "10.1145/3510003.3510096"),
    (ComputerOrgConfMapper, "https://www.computer.org/csdl/proceedings-article/icse/2022/922100a749/1Ems2zKEg8g"),
    (ComputerOrgJournalMapper, "https://www.computer.org/csdl/journal/ts/2022/02/09072287/1jbja34XYVW"),
    # this isn't needed for any venues right now, so no point in testing with other venue.
    # (HtmlParserMapper(), ""),
    (SpringerMapper, "10.1007/s10664-021-10043-z")
]

@pytest.mark.ip_restricted
@pytest.mark.parametrize("class_,doi", inputs)
def test_mapper(class_, doi):
    pdf_url = class_().get_pdf_url(doi)
    r = requests.get(pdf_url)
    r.raise_for_status()
    assert r.status_code == 200
    assert 'application/pdf' in r.headers.get('Content-Type')