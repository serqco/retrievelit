from abc import ABC, abstractmethod

class DoiMapper(ABC):
    """Abstract base class for mappers converting a DOI to a PDF download URL."""
    @abstractmethod
    def get_pdf_url(self, doi: str) -> str:
        """Return the PDF download URL for the DOI."""
        pass