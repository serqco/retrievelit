from dataclasses import dataclass
from abc import ABC, abstractmethod

DOI_URL_PREFIX = 'https://doi.org/'


@dataclass
class PDFDescriptor:
    download_url: str
    filename: str


def doi_url(doi: str) -> str:
    return f"{DOI_URL_PREFIX}{doi}"


class DoiMapper(ABC):
    """Abstract base class for mappers converting a DOI to a PDF download URL."""
    @abstractmethod
    def get_pdf_url(self, doi: str) -> str:
        """Return the PDF download URL for the DOI."""
        pass

    @abstractmethod
    def get_pdfdescriptor(self, doi: str) -> PDFDescriptor:
        """Return PDF download URL and filename for the DOI."""
        pass
