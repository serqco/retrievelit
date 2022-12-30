import utils
import doi_resolver

import pytest
from pytest_mock import MockerFixture

@pytest.mark.vcr
@pytest.mark.parametrize(
    "do_doi_rewrite, input_data, expected_result", 
    [
        pytest.param(
            False,
            [{"doi": "10.1007/s10664-014-9346-4"}],
            [{"doi": "10.1007/s10664-014-9346-4", "resolved_doi": "https://link.springer.com/article/10.1007/s10664-014-9346-4"}],
            id="without_ieee_rewrite",
        ),
        pytest.param(
            True,
            [{"doi": "10.1109/ICSE43902.2021.00018"}],
            [{"doi": "10.1109/ICSE43902.2021.00018", "resolved_doi": "https://www.computer.org/csdl/proceedings-article/icse/2021/029600a050/1sEXnte0Aow"}],
            id="with_ieee_rewrite"
        ),
        pytest.param(
            True,
            [{"doi": "10.1007/s10664-014-9346-4"}],
            [{"doi": "10.1007/s10664-014-9346-4", "resolved_doi": "https://link.springer.com/article/10.1007/s10664-014-9346-4"}],
            id="skip_ieee_rewrite_without_ieee_url"
        ),
        pytest.param(
            True,
            [{"doi": ""}],
            [{"doi": ""}],
            id="skip_entry_without_doi"
        )
    ]
)
def test_doi_resolving(do_doi_rewrite, input_data, expected_result, mocker):
    # don't wait between requests since they are read from cassettes
    doi_resolver.REQUEST_DELAY = 0
    resolver = doi_resolver.DoiResolver("", do_doi_rewrite)
    
    mocker.patch('utils.load_metadata', mocker.Mock(return_value=input_data))
    mocker.patch('utils.save_metadata')

    resolver.run()
    utils.save_metadata.assert_called_with("", expected_result)

def test_invalid_doi_throws_expection(mocker):
    resolver = doi_resolver.DoiResolver("", False)

    input_data = [{
        "doi": "invalid_doi"
    }]

    mocker.patch('utils.load_metadata', mocker.Mock(return_value=input_data))
    with pytest.raises(SystemExit):
        resolver.run()
