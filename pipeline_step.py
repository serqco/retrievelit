from abc import ABC, abstractmethod

class PipelineStep(ABC):
    
    @abstractmethod
    def run(self) -> None:
        pass