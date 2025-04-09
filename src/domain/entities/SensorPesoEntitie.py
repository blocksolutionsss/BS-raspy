from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from typing import List, ClassVar

@dataclass
class SensorPesoEntitie(QObject):
    # Definición de señales
    peso_changed = Signal(int)  # Señal que se emitirá cuando cambie la peso
    peso: int = 0
    def __init__(self):
        super().__init__()

    def update_weight(self, newPeso: int):
        self.peso = newPeso
        # Emitir señal de cambio
        self.peso_changed.emit(newPeso)