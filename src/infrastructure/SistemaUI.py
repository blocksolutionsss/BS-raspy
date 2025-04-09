from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QScrollArea, QHBoxLayout, QGroupBox, QFrame, QSplitter
from PySide6.QtCore import Signal, Qt, QTimer
from src.infrastructure.Sistema import Sistema
from ..application.services.SistemaService import SistemaService
from typing import Dict, List
import sys
from datetime import datetime

class SistemaUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sistema = Sistema()
        self.signals: Dict[str, Signal] = self.sistema.getSignals()
        
        # Configuración de la ventana principal
        self.setWindowTitle("Sistema de Monitoreo Industrial")
        self.setMinimumSize(900, 600)
        
        # Widget central y layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Panel de control
        self.crear_panel_control()
        
        # Panel de sensores
        self.crear_panel_sensores()
        
        # Panel de alertas y serial
        self.crear_panel_registros()
        
        # Almacenamiento de alertas (máximo 5)
        self.alertas: List[str] = []
        
        # Contador de pesos para distinguir entre Peso1 y Peso2
        self.contador_pesos = 0
        
        # Inicializar señales
        self.iniciar_señales()
        
    def crear_panel_control(self):
        """Crea el panel con botones de control del sistema"""
        panel_control = QGroupBox("Panel de Control")
        layout_control = QHBoxLayout()
        
        # Botón iniciar
        self.btn_iniciar = QPushButton("Iniciar Sistema")
        self.btn_iniciar.setMinimumHeight(40)
        self.btn_iniciar.clicked.connect(self.iniciar_sistema)
        layout_control.addWidget(self.btn_iniciar)
        
        # Botón detener
        self.btn_detener = QPushButton("Detener Sistema")
        self.btn_detener.setMinimumHeight(40)
        self.btn_detener.setEnabled(False)
        self.btn_detener.clicked.connect(self.detener_sistema)
        layout_control.addWidget(self.btn_detener)
        
        # Mostrador de hora
        self.lbl_hora = QLabel("Hora: 00:00")
        self.lbl_hora.setAlignment(Qt.AlignCenter)
        self.lbl_hora.setMinimumWidth(150)
        self.lbl_hora.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_control.addWidget(self.lbl_hora)
        
        panel_control.setLayout(layout_control)
        self.main_layout.addWidget(panel_control)
    
    def crear_panel_sensores(self):
        """Crea el panel que muestra los valores de los sensores"""
        panel_sensores = QGroupBox("Monitoreo de Sensores")
        layout_sensores = QHBoxLayout()
        
        # Sensor de temperatura
        grupo_temp = QGroupBox("Temperatura")
        layout_temp = QVBoxLayout()
        self.lbl_temperatura = QLabel("0.0 °C")
        self.lbl_temperatura.setAlignment(Qt.AlignCenter)
        self.lbl_temperatura.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_temp.addWidget(self.lbl_temperatura)
        grupo_temp.setLayout(layout_temp)
        layout_sensores.addWidget(grupo_temp)
        
        # Sensor de humedad
        grupo_hum = QGroupBox("Humedad")
        layout_hum = QVBoxLayout()
        self.lbl_humedad = QLabel("0.0 %")
        self.lbl_humedad.setAlignment(Qt.AlignCenter)
        self.lbl_humedad.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_hum.addWidget(self.lbl_humedad)
        grupo_hum.setLayout(layout_hum)
        layout_sensores.addWidget(grupo_hum)
        
        # Sensor de peso 1
        grupo_peso1 = QGroupBox("Peso Sensor 1")
        layout_peso1 = QVBoxLayout()
        self.lbl_peso1 = QLabel("0.0 kg")
        self.lbl_peso1.setAlignment(Qt.AlignCenter)
        self.lbl_peso1.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_peso1.addWidget(self.lbl_peso1)
        grupo_peso1.setLayout(layout_peso1)
        layout_sensores.addWidget(grupo_peso1)
        
        # Sensor de peso 2
        grupo_peso2 = QGroupBox("Peso Sensor 2")
        layout_peso2 = QVBoxLayout()
        self.lbl_peso2 = QLabel("0.0 kg")
        self.lbl_peso2.setAlignment(Qt.AlignCenter)
        self.lbl_peso2.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_peso2.addWidget(self.lbl_peso2)
        grupo_peso2.setLayout(layout_peso2)
        layout_sensores.addWidget(grupo_peso2)
        
        # Sensor de calidad de aire
        grupo_aire = QGroupBox("Calidad del Aire")
        layout_aire = QVBoxLayout()
        self.lbl_calidad_aire = QLabel("0.0 ppm")
        self.lbl_calidad_aire.setAlignment(Qt.AlignCenter)
        self.lbl_calidad_aire.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_aire.addWidget(self.lbl_calidad_aire)
        grupo_aire.setLayout(layout_aire)
        layout_sensores.addWidget(grupo_aire)
        
        panel_sensores.setLayout(layout_sensores)
        self.main_layout.addWidget(panel_sensores)

    def crear_panel_registros(self):
        """Crea el panel que muestra alertas y mensajes del serial"""
        panel_registros = QSplitter(Qt.Vertical)
        
        # Panel de alertas
        grupo_alertas = QGroupBox("Alertas del Sistema")
        layout_alertas = QVBoxLayout()
        self.area_alertas = QScrollArea()
        self.area_alertas.setWidgetResizable(True)
        self.widget_alertas = QWidget()
        self.layout_lista_alertas = QVBoxLayout(self.widget_alertas)
        self.area_alertas.setWidget(self.widget_alertas)
        layout_alertas.addWidget(self.area_alertas)
        grupo_alertas.setLayout(layout_alertas)
        panel_registros.addWidget(grupo_alertas)
        
        # Panel de mensajes serial
        grupo_serial = QGroupBox("Comunicación Serial")
        layout_serial = QVBoxLayout()
        self.area_serial = QScrollArea()
        self.area_serial.setWidgetResizable(True)
        self.widget_serial = QWidget()
        self.layout_lista_serial = QVBoxLayout(self.widget_serial)
        self.area_serial.setWidget(self.widget_serial)
        layout_serial.addWidget(self.area_serial)
        grupo_serial.setLayout(layout_serial)
        panel_registros.addWidget(grupo_serial)
        
        self.main_layout.addWidget(panel_registros, 1)  # Proporción de expansión

    def iniciar_sistema(self):
        """Inicia el sistema de monitoreo"""
        self.sistema.iniciar()
        self.btn_iniciar.setEnabled(False)
        self.btn_detener.setEnabled(True)
        self.agregar_alerta("Sistema iniciado correctamente", "info")

    def detener_sistema(self):
        """Detiene el sistema de monitoreo"""
        self.sistema.detener()
        self.btn_iniciar.setEnabled(True)
        self.btn_detener.setEnabled(False)
        self.agregar_alerta("Sistema detenido", "warning")

    def iniciar_señales(self):
        """Conecta las señales con sus respectivos slots"""
        # Labels que se actualizan con los valores de los sensores
        self.signals["Temperatura"].connect(self.actualizar_temperatura_ui)
        self.signals["Humedad"].connect(self.actualizar_humedad_ui)
        self.signals["Peso1"].connect(self.actualizar_peso_ui)
        self.signals["Peso2"].connect(self.actualizar_peso_ui)
        self.signals["CalidadAire"].connect(self.actualizar_calidad_ui)
        self.signals["time_actual"].connect(self.actualizar_hora_ui)
        
        # Alertas y serial
        self.signals["Alertas"].connect(self.mostrar_alerta)
        self.signals["Serial"].connect(self.mostrar_serial)
        self.signals["Pause"].connect(self.trigger_pause)

    def trigger_pause(self, status):
        print(status)
        if status:
            self.detener_sistema()
        else:
            self.iniciar_sistema()

    def actualizar_temperatura_ui(self, temperatura):
        """Actualiza el indicador de temperatura en la interfaz"""
        self.lbl_temperatura.setText(f"{temperatura:.1f} °C")
        # Cambiar color según rango
        if temperatura > 40:
            self.lbl_temperatura.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        elif temperatura < 10:
            self.lbl_temperatura.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        else:
            self.lbl_temperatura.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")

    def actualizar_humedad_ui(self, humedad):
        """Actualiza el indicador de humedad en la interfaz"""
        self.lbl_humedad.setText(f"{humedad:.1f} %")
        # Cambiar color según rango
        if humedad > 80:
            self.lbl_humedad.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        elif humedad < 20:
            self.lbl_humedad.setStyleSheet("font-size: 16px; font-weight: bold; color: orange;")
        else:
            self.lbl_humedad.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")

    def actualizar_peso_ui(self, peso):
        """Actualiza los indicadores de peso en la interfaz"""
        if self.contador_pesos % 2 == 0:
            self.lbl_peso1.setText(f"{peso:.1f} kg")
        else:
            self.lbl_peso2.setText(f"{peso:.1f} kg")
        self.contador_pesos += 1

    def actualizar_calidad_ui(self, calidad):
        """Actualiza el indicador de calidad de aire en la interfaz"""
        self.lbl_calidad_aire.setText(f"{calidad:.1f} ppm")
        # Cambiar color según rango
        if calidad > 1000:
            self.lbl_calidad_aire.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
            self.agregar_alerta(f"¡Alerta! Calidad de aire peligrosa: {calidad:.1f} ppm", "critical")
        elif calidad > 700:
            self.lbl_calidad_aire.setStyleSheet("font-size: 16px; font-weight: bold; color: orange;")
        else:
            self.lbl_calidad_aire.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")

    def actualizar_hora_ui(self, hora):
        """Actualiza el indicador de hora en la interfaz"""
        self.lbl_hora.setText(f"Hora: {hora}")

    def mostrar_alerta(self, mensaje):
        """Recibe alertas del sistema y las muestra en la interfaz"""
        self.agregar_alerta(mensaje, "warning")

    def agregar_alerta(self, mensaje, tipo):
        """Agrega una alerta al panel de alertas con formato según el tipo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        texto_alerta = f"[{timestamp}] {mensaje}"
        
        # Crear etiqueta para la alerta con estilo según el tipo
        lbl_alerta = QLabel(texto_alerta)
        if tipo == "critical":
            lbl_alerta.setStyleSheet("background-color: #ffcccc; padding: 8px; border: 1px solid #ff0000;")
        elif tipo == "warning":
            lbl_alerta.setStyleSheet("background-color: #fff3cd; padding: 8px; border: 1px solid #ffeeba;")
        elif tipo == "info":
            lbl_alerta.setStyleSheet("background-color: #d1ecf1; padding: 8px; border: 1px solid #bee5eb;")
        
        # Limitar a 5 alertas
        if len(self.alertas) >= 5:
            # Eliminar el widget más antiguo
            item = self.layout_lista_alertas.itemAt(0)
            if item:
                widget = item.widget()
                self.layout_lista_alertas.removeItem(item)
                widget.deleteLater()
            # Eliminar la alerta más antigua de la lista
            self.alertas.pop(0)
        
        # Agregar la nueva alerta
        self.layout_lista_alertas.addWidget(lbl_alerta)
        self.alertas.append(texto_alerta)
        
        # Asegurarse de que la nueva alerta sea visible
        self.area_alertas.verticalScrollBar().setValue(
            self.area_alertas.verticalScrollBar().maximum()
        )

    def mostrar_serial(self, mensaje):
        """Muestra mensajes del serial en formato de consola"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        texto_serial = f"[{timestamp}] {mensaje}"
        
        lbl_serial = QLabel(texto_serial)
        lbl_serial.setStyleSheet("font-family: monospace; padding: 2px;")
        
        # Limitar a 20 líneas
        if self.layout_lista_serial.count() >= 20:
            item = self.layout_lista_serial.itemAt(0)
            if item:
                widget = item.widget()
                self.layout_lista_serial.removeItem(item)
                widget.deleteLater()
        
        self.layout_lista_serial.addWidget(lbl_serial)
        
        # Desplazar al final para mostrar el mensaje más reciente
        self.area_serial.verticalScrollBar().setValue(
            self.area_serial.verticalScrollBar().maximum()
        )
