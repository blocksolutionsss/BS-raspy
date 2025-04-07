from src.domain.ports.SistemaRepository import SistemaRepository

class SistemaService:
    def __init__(self, repository: SistemaRepository):
        self.repository: SistemaRepository = repository

    def leerTemperaturas(self):
        try:
            self.repository.leerTemperaturas()
        except Exception as error:
            print(f"Hubo un error al leer las temperaturas: ${error}")

    def getSignals(self):
        try:
            return self.repository.getSignals()
        except Exception as error:
            print(f"Hubo un error al obtener las señakles: ${error}")