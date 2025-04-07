from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from PySide6.QtCore import Signal, Qt, QTimer
from src.infrastructure.Sistema import Sistema
from ..application.services.SistemaService import SistemaService
from typing import Dict
import sys

class SistemaUI(QMainWindow):
    def __init__(self):
        super().__init__()
        s = Sistema()
        self.repository = SistemaService(s)

        self.signals: Dict[str, Signal] = self.repository.getSignals()

        self.setWindowTitle("Sistema de Monitoreo")
        self.setGeometry(100, 100, 400, 200)  # x, y, ancho, alto
        
        # Configurar el widget central y layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Añadir etiquetas
        self.titulo_label = QLabel("Sistema de Monitoreo")
        self.titulo_label.setAlignment(Qt.AlignCenter)
        self.titulo_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.titulo_label)
        
        self.temperatura_label = QLabel("Temperatura: -- °C")
        self.temperatura_label.setAlignment(Qt.AlignCenter)
        self.temperatura_label.setStyleSheet("font-size: 24pt; color: #1e88e5;")
        self.layout.addWidget(self.temperatura_label)
        
        self.alerta_label = QLabel("")
        self.alerta_label.setAlignment(Qt.AlignCenter)
        self.alerta_label.setStyleSheet("font-size: 14pt; color: #f44336;")
        self.layout.addWidget(self.alerta_label)
        
        # Botones de control
        self.boton_iniciar = QPushButton("Iniciar Monitoreo")
        self.boton_iniciar.clicked.connect(self.iniciar_monitoreo)
        self.layout.addWidget(self.boton_iniciar)
        
        self.boton_detener = QPushButton("Detener Monitoreo")
        self.boton_detener.clicked.connect(self.detener_monitoreo)
        self.boton_detener.setEnabled(False)
        self.layout.addWidget(self.boton_detener)
        
        # Inicializar señales
        self.iniciar_señales()
        
        # Variables para control de alarmas
        self.alerta_timer = QTimer()
        self.alerta_timer.timeout.connect(self.parpadear_alerta)
        self.alerta_visible = True
        self.parpadeo_contador = 0

    def iniciar_señales(self):
        """Conecta las señales con sus respectivos slots"""
        self.signals["Temp"].connect(self.actualizar_temperatura_ui)
        
        # Si tienes otras señales, también las conectarías aquí
        # Por ejemplo:
        # self.signals["Humedad"].connect(self.actualizar_humedad_ui)
    
    def actualizar_temperatura_ui(self, valor: int):
        """Slot que se ejecuta cuando cambia la temperatura"""
        # Constantes de límites de temperatura
        TEMPERATURA_MINIMA = 50.0
        TEMPERATURA_MAXIMA = 75.0
        
        # Cambiar el color según la temperatura
        color = "#1e88e5"  # Azul por defecto
        if valor > TEMPERATURA_MAXIMA:
            color = "#f44336"  # Rojo para temperatura alta
            self.mostrar_alerta(f"Temperatura por encima del máximo", valor)
        elif valor < TEMPERATURA_MINIMA:
            color = "#4caf50"  # Verde para temperatura baja
            self.mostrar_alerta(f"Temperatura por debajo del mínimo", valor)
        else:
            # Limpiar alerta si la temperatura vuelve a valores normales
            self.alerta_label.setText("")
            if self.alerta_timer.isActive():
                self.alerta_timer.stop()
                self.alerta_label.setVisible(True)
        
        # Actualizar texto y estilo
        self.temperatura_label.setText(f"Temperatura: {valor} °C")
        self.temperatura_label.setStyleSheet(f"font-size: 24pt; color: {color};")
    
    def mostrar_alerta(self, mensaje: str, valor: int):
        """Muestra una alerta en la interfaz"""
        self.alerta_label.setText(f"ALERTA: {mensaje} ({valor} °C)")
        
        # Iniciar efecto de parpadeo si no está activo
        if not self.alerta_timer.isActive():
            self.parpadeo_contador = 0
            self.alerta_timer.start(500)  # Parpadeo cada 500ms
    
    def parpadear_alerta(self):
        """Hace parpadear el texto de alerta"""
        self.alerta_visible = not self.alerta_visible
        self.alerta_label.setVisible(self.alerta_visible)
        
        # Detener el parpadeo después de 5 segundos
        self.parpadeo_contador += 1
        if self.parpadeo_contador > 10:  # 5 segundos (10 * 500ms)
            self.alerta_timer.stop()
            self.alerta_label.setVisible(True)
            self.parpadeo_contador = 0
    
    def iniciar_monitoreo(self):
        """Inicia el monitoreo de temperatura"""
        try:
            self.repository.iniciar_monitoreo()
            self.boton_iniciar.setEnabled(False)
            self.boton_detener.setEnabled(True)
            print("Monitoreo iniciado")
        except Exception as e:
            print(f"Error al iniciar monitoreo: {str(e)}")
    
    def detener_monitoreo(self):
        """Detiene el monitoreo de temperatura"""
        try:
            self.repository.detener_monitoreo()
            self.boton_iniciar.setEnabled(True)
            self.boton_detener.setEnabled(False)
            print("Monitoreo detenido")
        except Exception as e:
            print(f"Error al detener monitoreo: {str(e)}")


# Código para ejecutar la aplicación si se ejecuta directamente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = SistemaUI()
    ventana.show()
    sys.exit(app.exec())