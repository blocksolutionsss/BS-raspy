from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from typing import List, ClassVar

@dataclass
class SensorHumedadEntitie(QObject):
    # Definición de señales
    humedad_changed = Signal(int)  # Señal que se emitirá cuando cambie la humedad
    humedad: int = 0
    def __init__(self):
        super().__init__()

    def update_Humedad(self, newHumedad: int):
        self.humedad = newHumedad
        # Emitir señal de cambio
        self.humedad_changed.emit(newHumedad)