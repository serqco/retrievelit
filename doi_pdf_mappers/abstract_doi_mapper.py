from abc import ABC, abstractmethod

class DoiMapper(ABC):
    
    @abstractmethod
    def get_pdf_url(self, doi):
        pass