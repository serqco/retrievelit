from abc import ABC, abstractmethod

class ResolvedDoiMapper(ABC):
    """Abstract base class for mappers converting a resolved DOI to a PDF download URL."""
    @abstractmethod
    def get_pdf_url(self, resolved_doi: str) -> str:
        """Return the PDF download URL for the resolved DOI."""
        pass