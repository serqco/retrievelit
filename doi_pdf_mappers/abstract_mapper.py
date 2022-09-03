from abc import ABC, abstractmethod

class Mapper(ABC):
    
    @abstractmethod
    def get_pdf_url(self, doi, resolved_doi):
        pass