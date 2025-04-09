from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass, field
from typing import List

@dataclass
class AlertasEntitie(QObject):
    alertas_changed = Signal(list)  # Emitimos la lista actualizada

    alertas: List[dict] = field(default_factory=list)

    def __init__(self):
        super().__init__()
        self.alertas = []

    def update_alertas(self, new_alerta: dict):
        if len(self.alertas) >= 5:
            self.alertas.pop(0)  # Elimina la más antigua
        self.alertas.append(new_alerta)
        self.alertas_changed.emit(self.alertas)
