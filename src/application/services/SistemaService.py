from src.domain.ports.SistemaRepository import SistemaRepository

class SistemaService:
    def __init__(self, repository: SistemaRepository):
        self.repository: SistemaRepository = repository

    def iniciar(self):
        try:
            self.repository.iniciar()
        except Exception as error:
            print(f"Hubo un error al iniciar el sistema: ${error}")
            
    def detener(self):
        try:
            self.repository.detener()
        except Exception as error:
            print(f"Hubo un error al detener el sistema: ${error}")

    def getSignals(self):
        try:
            return self.repository.getSignals()
        except Exception as error:
            print(f"Hubo un error al obtener las señakles: ${error}")