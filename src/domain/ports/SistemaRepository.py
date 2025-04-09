from abc import ABC, abstractmethod

class SistemaRepository(ABC):

    @abstractmethod
    def iniciar(self):
        pass
    
    @abstractmethod
    def detener(self):
        pass

    @abstractmethod
    def getSignals(self):
        pass