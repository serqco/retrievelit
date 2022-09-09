from abc import ABC, abstractmethod

class ResolvedDoiMapper(ABC):
    
    @abstractmethod
    def get_pdf_url(self, resolved_doi):
        pass