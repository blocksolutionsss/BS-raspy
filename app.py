from src.infrastructure.SistemaUI import SistemaUI
from src.infrastructure.Sistema import Sistema
from src.application.services.SistemaService import SistemaService
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sistema_ui = SistemaUI()
    sistema_ui.show()
    sys.exit(app.exec())

    # sistema = SistemaService(Sistema())
    # sistema.iniciar()