import textwrap
import bibtex_builder

from pytest_mock import MockerFixture

def test_bibtex(mocker: MockerFixture) -> None:
    bibtex_builder_ = bibtex_builder.BibtexBuilder("mocked", "mocked")
    input_data = [{
        "identifier": "identifier",
        "title": "title",
        "venue": "venue",
        "volume": "volume",
        "number": "number",
        "pages": "3-5",
        "year": "2021",
        "type": "Conference Paper",
        "doi": "12.3456/7.891011",
        "authors": [
            "John Doe",
            "Jane Doe"
        ],
    }]
    expected_data = textwrap.dedent("""\
        @article{identifier,
         author = {John Doe and Jane Doe},
         doi = {12.3456/7.891011},
         number = {number},
         pages = {3-5},
         title = {title},
         type = {Conference Paper},
         venue = {venue},
         volume = {volume},
         year = {2021}
        }
    """)
    
    mocker.patch('utils.load_metadata', mocker.Mock(return_value=input_data))
    open_mock = mocker.mock_open()
    mocker.patch('builtins.open', open_mock)
    bibtex_builder_.run()
    open_mock.return_value.write.assert_called_once_with(expected_data)
