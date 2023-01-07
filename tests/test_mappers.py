import requests
import pytest

from retrievelit.doi_pdf_mappers.acm import AcmMapper
from retrievelit.doi_pdf_mappers.computer_org_conf import ComputerOrgConfMapper
from retrievelit.doi_pdf_mappers.computer_org_journal import ComputerOrgJournalMapper
# from retrievelit.doi_pdf_mappers.html_parser import HtmlParserMapper
from retrievelit.doi_pdf_mappers.springer import SpringerMapper
from retrievelit.doi_pdf_mappers.scihub import ScihubMapper

inputs = [
    (AcmMapper, "10.1145/3510003.3510096"),
    (ComputerOrgConfMapper, "https://www.computer.org/csdl/proceedings-article/icse/2022/922100a749/1Ems2zKEg8g"),
    (ComputerOrgJournalMapper, "https://www.computer.org/csdl/journal/ts/2022/02/09072287/1jbja34XYVW"),
    # this isn't needed for any venues right now, so no point in testing with other venue.
    # (HtmlParserMapper(), ""),
    (SpringerMapper, "10.1007/s10664-021-10043-z"),
    (ScihubMapper, "10.1016/j.infsof.2016.09.011")
]

@pytest.mark.ip_restricted
@pytest.mark.parametrize("class_,doi", inputs)
def test_mapper(class_, doi):
    """Test if the mappers return URLs that point to PDF data."""
    pdf_url = class_().get_pdf_url(doi)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'}
    r = requests.get(pdf_url, headers=headers)
    r.raise_for_status()
    assert r.status_code == 200
    assert 'application/pdf' in r.headers.get('Content-Type')