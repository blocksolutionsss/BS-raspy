from abc import ABC, abstractmethod

class SistemaRepository(ABC):

    @abstractmethod
    def leerTemperaturas(self):
        pass

    @abstractmethod
    def getSignals(self):
        pass