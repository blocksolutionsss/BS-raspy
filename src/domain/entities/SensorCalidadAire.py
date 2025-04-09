from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from typing import List, ClassVar

@dataclass
class SensorCalidadAire(QObject):
    # Definición de señales
    calidad_Aire_changed = Signal(int)  # Señal que se emitirá cuando cambie la calidad_Aire
    calidad_Aire: int = 0
    def __init__(self):
        super().__init__()

    def update_Calidad_Aire(self, newCalidad_Aire: int):
        self.calidad_Aire = newCalidad_Aire
        # Emitir señal de cambio
        self.calidad_Aire_changed.emit(newCalidad_Aire)