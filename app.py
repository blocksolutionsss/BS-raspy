from src.infrastructure.SistemaUI import SistemaUI
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = SistemaUI()
    ventana.show()
    sys.exit(app.exec())