from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from typing import List, ClassVar

@dataclass
class SensorTemperaturaEntitie(QObject):
    # Definición de señales
    temperatura_changed = Signal(int)  # Señal que se emitirá cuando cambie la temperatura
    temperatura_alert = Signal(str, int)  # Señal para alertas (mensaje, valor)

    TEMPERATURA_MINIMA: float = 50.0
    TEMPERATURA_MAXIMA: float = 75.0
    def __init__(self):
        super().__init__()
        self.temperatura: int = 0

    def update_temperature(self, newTemp: int):
        self.temperatura = newTemp
        # Emitir señal de cambio
        self.temperatura_changed.emit(newTemp)