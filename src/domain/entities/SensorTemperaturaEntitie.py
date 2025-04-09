from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from typing import List, ClassVar

@dataclass
class SensorTemperaturaEntitie(QObject):
    # Definición de señales
    temperatura_changed = Signal(int)  # Señal que se emitirá cuando cambie la temperatura
    temperatura: int = 0
    def __init__(self):
        super().__init__()

    def update_temperature(self, newTemp: int):
        self.temperatura = newTemp
        # Emitir señal de cambio
        self.temperatura_changed.emit(newTemp)