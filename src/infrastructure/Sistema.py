from src.domain.entities.SensorTemperaturaEntitie import SensorTemperaturaEntitie
from src.domain.entities.ESP32Entitie import ESP32Entitie
from src.domain.entities.SQLite3Entitie import SQLite3Entitie
from src.domain.entities.SensorPesoEntitie import SensorPesoEntitie
from src.domain.entities.SensorCalidadAire import SensorCalidadAire
from src.domain.entities.SensorHumedadEntitie import SensorHumedadEntitie
from src.domain.entities.AlertasEntitie import AlertasEntitie
from src.domain.entities.SocketIOEntitie import SocketIOEntitie
from src.domain.entities.DeviceEntitie import DeviceEntitie
from threading import Thread, Lock
from datetime import datetime, timedelta
from serial import Serial, SerialException
import time
import random
from ..domain.entities.BrokerEntitie import BrokerEntitie

class Sistema:
    def __init__(self):
        self.sensorTemperatura = SensorTemperaturaEntitie()
        self.sensorHumedad = SensorHumedadEntitie()
        self.sensorPeso1 = SensorPesoEntitie()
        self.sensorPeso2 = SensorPesoEntitie()
        self.sensorCalidadAire = SensorCalidadAire()
        self.alertas = AlertasEntitie()
        
        self.running = False
        self.time_init = datetime.now()
        self.time_finish = datetime.now()
        self.sqlite = SQLite3Entitie()
        self.device = DeviceEntitie(self.sqlite.get_device())
        self.socketIO = SocketIOEntitie(self.esp32, self.device)
        
        self.broker = BrokerEntitie()
        
        self.device_ID = "device10"
        
        self.lock = Lock()
        self.threads = []
        
        self.esp32 = ESP32Entitie()
        self.thread_esp32 = Thread(target=self.leerSerial, daemon=True)
        self.thread_esp32.start()
        
        self.data = {
            "alert": {},
            "real-time": {},
            "End":{}
        }

    def temporizador(self):
        """Simula un temporizador"""
        while True:
            if not self.device.get("pause", True):
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
                        'hours_actual': self.device["hours_actual"],
                        'minute_actual': self.device["minute_actual"]
                    })

                    if segundos_actuales >= segundos_totales:
                        print("Tiempo de deshidratado alcanzado.")
                        # Guardar los nuevos valores en la base de datos
                        self.device["pause"] = True
                        self.sqlite.update_device({
                            'pause': self.device["pause"]
                        })

            time.sleep(1)

        print("Tiempo de deshidratado finalizado.")

        
    def iniciar(self):
        """Inicia el proceso de desidratado"""
        self.esp32.iniciar_monitoreo(self.device["temperature"], self.device["humidity"])
        self.running = True
        self.device["pause"] = False
        self.sqlite.update_device({
            'pause': self.device["pause"]
        })
        self.time_init = datetime.now()
        
        # Iniciar el hilo para la lectura de datos del ESP32
        self.threads.append(Thread(target=self.leerSerial, daemon=True))
        
        # Iniciar el hilo para la lectura de datos del ESP32
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
        """Detiene el proceso de desidratado"""
        self.esp32.pausar_monitoreo()
        self.running_temporizador = False
        self.device["pause"] = True
        self.sqlite.update_device({
            'pause': self.device["pause"]
        })
        self.time_finish = datetime.now()
    
    def leerEnd(self):
        """Simula la lectura de datos del ESP32"""
        while self.running:
            try:
                if self.data["End"] == {}:
                    continue
                with self.lock:
                    self.data["End"] = {}
                time.sleep(1)
            except:
              print('An exception occurred')
        
    def leerRealTime(self):
        """Simula la lectura de datos del ESP32"""
        while self.running:
            try:
                if self.data["real-time"] == {}:
                    continue
                with self.lock:
                    payload = {
                        "device": self.device_ID,
                        "real-time": self.data["real-time"]
                    }
                    self.broker.publish('bs.real-time', payload)
                    
                    # Obtener la fecha y hora actual
                    date = datetime.now().strftime('%H:%M')
                    
                    temperature = self.data["real-time"]["temperature"]
                    humidity = self.data["real-time"]["humidity"]
                    weight1 = self.data["real-time"]["weight1"]
                    weight2 = self.data["real-time"]["weight2"]
                    flyClean = self.data["real-time"]["flyClean"]
                    
                    self.sqlite.add_reading({"value": temperature, "time": date}, "temperatures")
                    self.sensorTemperatura.update_temperature(temperature)
                    
                    self.sqlite.add_reading({"value": humidity, "time": date}, "humidities")
                    self.sensorHumedad.update_Humedad(humidity)
                    
                    self.sqlite.add_reading({"value": weight1, "time": date}, "weights1")
                    self.sensorPeso1.update_weight(weight1)
                    
                    self.sqlite.add_reading({"value": weight2, "time": date}, "weights2")
                    self.sensorPeso2.update_weight(weight2)
                    
                    self.sqlite.add_reading({"value": flyClean, "time": date}, "airValues")
                    self.sensorCalidadAire.update_Calidad_Aire(flyClean)
                    
                    payload = {
                        "device": self.device_ID,
                        "data": {
                            "temperature": self.data["real-time"]["temperature"],
                            "humidity": self.data["real-time"]["humidity"],
                            "weight1": self.data["real-time"]["weight1"],
                            "weight2": self.data["real-time"]["weight2"],
                            "airPurity": self.data["real-time"]["flyClean"],
                            "hours_actual": self.device["hours_actual"],
                            "minute_actual": self.device["minute_actual"],
                        }
                    }
                    self.broker.publish('bs.real-time', payload)
                    
                    self.data["real-time"] = {}
                time.sleep(1)
            except:
              print('An exception occurred')

    def leerAlertas(self):
        """Simula la lectura de temperatura"""
        while self.running:
            try:
                if not self.data.get("alert"):
                    continue
                with self.lock:
                    payload = {
                        "device": self.device_ID,
                        "alerts": self.data["alert"]
                    }
                    self.broker.publish('bs.notifications', payload)
                    
                    # Obtener la fecha y hora actual
                    date = datetime.now().strftime('%H:%M')
                    for alert in self.data["alert"]:
                        alert["date"] = date
                        alert["id"] = self.sqlite.add_alert(alert)
                        self.alertas.add_alert(alert)
                    
                    payload = {
                        "device": self.device_ID,
                        "alerts": self.data["alert"]
                    }
                    self.broker.publish('bs.alertas', payload)
                    
                    self.data["alert"] = {}
                time.sleep(1)
            except:
              print('An exception occurred')
    
    def leerSerial(self):
        """Simula la lectura de datos del ESP32"""
        while self.running:
            try:
                if self.esp32.serial.in_waiting == 0:
                    continue
                data = self.esp32.serial.readline().decode('utf-8').strip() 
                self.esp32.update_serial_data(str(data))
                if "alert" in data:
                    self.data["alert"] = data["alert"]
                elif "real-time" in data:
                    self.data["real-time"] = data["real-time"]
                elif "End" in data:
                    self.data["End"] = data["End"]
                    
                print(f"Datos leídos del ESP32: {data}")
                
            except SerialException as e:
                print(f"Error de conexión: {e}")
            except Exception as e:
                print(f"Ocurrió un error inesperado: {e}")

    def getSignals(self):
        return {
            "Temperatura": self.sensorTemperatura.temperatura_changed,
            "Humedad": self.sensorHumedad.humedad_changed,
            "Peso1": self.sensorPeso1.peso_changed,
            "Peso2": self.sensorPeso2.peso_changed,
            "CalidadAire": self.sensorCalidadAire.calidad_Aire_changed,
            "time_actual": self.device.timeActualChanged,
            "Alertas": self.alertas.alertas_changed,
            "Serial": self.esp32.serial_data_changed,
        }
    