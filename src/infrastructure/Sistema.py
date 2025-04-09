from src.domain.entities.SensorTemperaturaEntitie import SensorTemperaturaEntitie
from src.domain.entities.ESP32Entitie import ESP32Entitie
from src.domain.entities.SQLite3Entitie import SQLite3Entitie
from src.domain.entities.SensorPesoEntitie import SensorPesoEntitie
from src.domain.entities.SensorCalidadAire import SensorCalidadAire
from src.domain.entities.SensorHumedadEntitie import SensorHumedadEntitie
from src.domain.entities.AlertasEntitie import AlertasEntitie
from src.domain.entities.SocketIOEntitie import SocketIOEntitie
from src.domain.entities.DeviceEntitie import DeviceEntitie
from src.domain.entities.BrokerEntitie import BrokerEntitie
from threading import Thread, Lock
from datetime import datetime, timedelta
from serial import Serial, SerialException
import time
import random
import json

class Sistema:
    def __init__(self):
        self.sensorTemperatura = SensorTemperaturaEntitie()
        self.sensorHumedad = SensorHumedadEntitie()
        self.sensorPeso1 = SensorPesoEntitie()
        self.sensorPeso2 = SensorPesoEntitie()
        self.sensorCalidadAire = SensorCalidadAire()
        self.alertas = AlertasEntitie()
        
        self.broker = BrokerEntitie()
        
        self.device_ID = "device10"
        
        self.lock = Lock()
        self.threads = []
        
        self.esp32 = ESP32Entitie()
        self.running = False
        self.running_temporizador = False
        self.time_init = datetime.now()
        self.time_finish = datetime.now()
        self.sqlite = SQLite3Entitie()
        self.device = DeviceEntitie(self.sqlite.get_device())
        self.socketIO = SocketIOEntitie(self.esp32, self.device)
        
        self.data = {
            "alert": {},
            "real-time": {},
            "End": {}
        }

    def temporizador(self):
        """Simula un temporizador"""
        while self.running_temporizador:
            if not self.device.get_pause():
                with self.lock:
                    # Calcular los segundos totales del tiempo objetivo
                    segundos_totales = (self.device.get_hours() * 3600) + (self.device.get_minutes() * 60)

                    # Calcular los segundos actuales
                    segundos_actuales = (self.device.get_hours_actual() * 3600) + (self.device.get_minute_actual() * 60) + 1
                    # Actualizar los valores actuales en device
                    self.device.set_hours_actual(segundos_actuales // 3600)
                    self.device.set_minute_actual((segundos_actuales % 3600) // 60)

                    # Guardar los nuevos valores en la base de datos
                    self.sqlite.update_device({
                        'hours_actual': self.device.get_hours_actual(),
                        'minute_actual': self.device.get_minute_actual()
                    })

                    if segundos_actuales >= segundos_totales:
                        print("Tiempo de deshidratado alcanzado.")
                        # Guardar los nuevos valores en la base de datos
                        self.device.set_pause(True)
                        self.sqlite.update_device({
                            'pause': self.device.get_pause()
                        })

            time.sleep(1)

        print("Tiempo de deshidratado finalizado.")

        
    def iniciar(self):
        """Inicia el proceso de deshidratado"""
        self.esp32.iniciar_monitoreo(self.device.get_temperature(), self.device.get_humidity())
        self.running = True
        self.running_temporizador = True
        self.device.set_pause(False)
        self.sqlite.update_device({
            'pause': False
        })
        self.time_init = datetime.now()
        
        # Detener hilos anteriores si existen
        self.threads = []
        
        # Iniciar el hilo para la lectura de datos del ESP32
        self.threads.append(Thread(target=self.leerSerial, daemon=True))
        
        # Iniciar el hilo para la lectura de alertas
        self.threads.append(Thread(target=self.leerAlertas, daemon=True))
        
        # Iniciar el hilo para cambios de real-time
        self.threads.append(Thread(target=self.leerRealTime, daemon=True))
        
        # Iniciar el hilo para cambios de End
        self.threads.append(Thread(target=self.leerEnd, daemon=True))
        
        # Iniciar el hilo para el temporizador
        self.threads.append(Thread(target=self.temporizador, daemon=True))
        
        for t in self.threads:
            t.start()
        
    def detener(self):
        """Detiene el proceso de deshidratado"""
        self.esp32.pausar_monitoreo()
        self.running = False
        self.running_temporizador = False
        self.device.set_pause(True)
        self.sqlite.update_device({
            'pause': True
        })
        self.time_finish = datetime.now()
    
    def leerEnd(self):
        """Monitorea señales de finalización"""
        while self.running:
            try:
                if self.data["End"] == {}:
                    time.sleep(1)
                    continue
                
                with self.lock:
                    self.data["End"] = {}
                    self.detener()
            except Exception as e:
                print(f'Error en leerEnd: {e}')
            time.sleep(1)
        
    def leerRealTime(self):
        """Procesa datos en tiempo real del ESP32"""
        while self.running:
            try:
                if self.data["real-time"] == {}:
                    time.sleep(1)
                    continue
                
                with self.lock:
                    # Obtener la fecha y hora actual
                    date = datetime.now().strftime('%H:%M')
                    
                    # Extraer valores
                    temperatura = self.data["real-time"].get("temperature", 0)
                    humedad = self.data["real-time"].get("humidity", 0)
                    peso1 = self.data["real-time"].get("weight1", 0)
                    peso2 = self.data["real-time"].get("weight2", 0)
                    calidadAire = self.data["real-time"].get("flyClean", 0)
                    
                    # Publicar datos iniciales
                    payload = {
                        "device": self.device_ID,
                        "real-time": self.data["real-time"]
                    }
                    self.broker.publish('bs.real-time', payload)
                    
                    # Actualizar sensores y guardar en SQLite
                    self.sqlite.add_reading({"value": temperatura, "time": date}, "temperatures")
                    self.sensorTemperatura.update_temperature(temperatura)
                    
                    self.sqlite.add_reading({"value": humedad, "time": date}, "humidities")
                    self.sensorHumedad.update_Humedad(humedad)
                    
                    self.sqlite.add_reading({"value": peso1, "time": date}, "weights1")
                    self.sensorPeso1.update_weight(peso1)
                    
                    self.sqlite.add_reading({"value": peso2, "time": date}, "weights2")
                    self.sensorPeso2.update_weight(peso2)
                    
                    self.sqlite.add_reading({"value": calidadAire, "time": date}, "airValues")
                    self.sensorCalidadAire.update_Calidad_Aire(calidadAire)
                    
                    # Preparar y publicar payload completo
                    payload_completo = {
                        "device": self.device_ID,
                        "data": {
                            "temperature": temperatura,
                            "humidity": humedad,
                            "weight1": peso1,
                            "weight2": peso2,
                            "airPurity": calidadAire,
                            "hours_actual": self.device.get_hours_actual(),
                            "minute_actual": self.device.get_minute_actual(),
                        }
                    }
                    self.broker.publish('bs.real-time', payload_completo)
                    
                    # Limpiar datos procesados
                    self.data["real-time"] = {}
            except Exception as e:
                print(f'Error en leerRealTime: {e}')
            time.sleep(1)

    def leerAlertas(self):
        """Procesa alertas del ESP32"""
        while self.running:
            try:
                if not self.data.get("alert") or self.data["alert"] == {}:
                    time.sleep(1)
                    continue
                
                with self.lock:
                    # Publicar alertas iniciales
                    payload = {
                        "device": self.device_ID,
                        "alerts": self.data["alert"]
                    }
                    self.broker.publish('bs.notifications', payload)
                    
                    # Procesar cada alerta
                    date = datetime.now().strftime('%H:%M')
                    alertas_procesadas = []
                    
                    # Verificar si es una lista o un solo objeto
                    if isinstance(self.data["alert"], list):
                        alertas_a_procesar = self.data["alert"]
                    else:
                        alertas_a_procesar = [self.data["alert"]]
                    
                    for alerta in alertas_a_procesar:
                        # Si es un diccionario, procesarlo
                        if isinstance(alerta, dict):
                            alerta["date"] = date
                            alerta_id = self.sqlite.add_alert(alerta)
                            alerta["id"] = alerta_id
                            self.alertas.add_alert(alerta)
                            alertas_procesadas.append(alerta)
                    
                    # Publicar alertas procesadas
                    if alertas_procesadas:
                        payload_final = {
                            "device": self.device_ID,
                            "alerts": alertas_procesadas
                        }
                        self.broker.publish('bs.alertas', payload_final)
                    
                    # Limpiar alertas procesadas
                    self.data["alert"] = {}
            except Exception as e:
                print(f'Error en leerAlertas: {e}')
            time.sleep(1)
    
    def leerSerial(self):
        """Lee datos del puerto serial del ESP32"""
        while self.running:
            try:
                if not self.esp32.serial.is_open:
                    self.esp32.iniciar_monitoreo(self.device.get_temperature(), self.device.get_humidity())
                    time.sleep(1)
                    continue
                
                if self.esp32.serial.in_waiting == 0:
                    time.sleep(0.1)
                    continue
                
                # Leer datos del serial
                data_str = self.esp32.serial.readline().decode('utf-8').strip()
                self.esp32.update_serial_data(data_str)
                
                # Intentar parsear como JSON
                try:
                    data = json.loads(data_str)
                    
                    # Distribuir datos según su tipo
                    if "alert" in data:
                        self.data["alert"] = data["alert"]
                    elif "real-time" in data:
                        self.data["real-time"] = data["real-time"]
                    elif "End" in data:
                        self.data["End"] = data["End"]
                    
                    print(f"Datos leídos del ESP32: {data}")
                except json.JSONDecodeError:
                    # Si no es JSON, simplemente registrarlo como mensaje
                    print(f"Datos recibidos (no JSON): {data_str}")
                    
            except SerialException as e:
                print(f"Error de conexión serial: {e}")
                time.sleep(5)  # Esperar antes de reintentar
            except Exception as e:
                print(f"Error inesperado en leerSerial: {e}")
                time.sleep(1)

    def getSignals(self):
        """Retorna las señales disponibles para la interfaz de usuario"""
        return {
            "Temperatura": self.sensorTemperatura.temperatura_changed,
            "Humedad": self.sensorHumedad.humedad_changed,
            "Peso1": self.sensorPeso1.peso_changed,
            "Peso2": self.sensorPeso2.peso_changed,
            "CalidadAire": self.sensorCalidadAire.calidad_Aire_changed,
            "time_actual": self.device.timeActualChanged,
            "Alertas": self.alertas.alertas_changed,
            "Serial": self.esp32.serial_data_changed,
            "Pause": self.device.pauseChanged,
        }