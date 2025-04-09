from src.domain.entities.SensorTemperaturaEntitie import SensorTemperaturaEntitie
from src.domain.entities.ESP32Entitie import ESP32Entitie
from src.domain.entities.SQLite3Entitie import SQLite3Entitie
from threading import Thread, Lock
from datetime import datetime, timedelta
from serial import Serial, SerialException
import time
import random
from ..domain.entities.BrokerEntitie import BrokerEntitie

class Sistema:
    def __init__(self):
        self.sensorTemp = SensorTemperaturaEntitie()
        
        self.running = False
        self.time_init = datetime.now()
        self.time_finish = datetime.now()
        self.sqlite = SQLite3Entitie()
        self.device_data = self.sqlite.get_device()
        
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
        
    def iniciar(self):
        """Inicia el proceso de desidratado"""
        self.esp32.iniciar_monitoreo(self.device_data["temperature"], self.device_data["humidity"])
        self.running = True
        self.time_init = datetime.now()
        
        # Iniciar el hilo para la lectura de datos del ESP32
        self.threads.append(Thread(target=self.leerAlertas, daemon=True))
        
        # Iniciar el hilo para cambios de real-time
        self.threads.append(Thread(target=self.leerRealTime, daemon=True))
        
        # Iniciar el hilo para cambios de End
        self.threads.append(Thread(target=self.leerEnd, daemon=True))
        
        for t in self.threads:
            t.start()
        
    def detener(self):
        """Detiene el proceso de desidratado"""
        self.esp32.pausar_monitoreo()
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
                    
                    self.sqlite.add_reading({"value": self.data["real-time"]["temperature"], "time": date}, "temperatures")
                    self.sqlite.add_reading({"value": self.data["real-time"]["humidity"], "time": date}, "humidities")
                    self.sqlite.add_reading({"value": self.data["real-time"]["weight1"], "time": date}, "weights1")
                    self.sqlite.add_reading({"value": self.data["real-time"]["weight2"], "time": date}, "weights2")
                    self.sqlite.add_reading({"value": self.data["real-time"]["flyClean"], "time": date}, "airValues")
                    
                    payload = {
                        "device": self.device_ID,
                        "data": {
                            "temperature": self.data["real-time"]["temperature"],
                            "humidity": self.data["real-time"]["humidity"],
                            "weight1": self.data["real-time"]["weight1"],
                            "weight2": self.data["real-time"]["weight2"],
                            "flyClean": self.data["real-time"]["flyClean"],
                            "date": date
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
                    
                    payload = {
                        "device": self.device_ID,
                        "alerts": self.data["alert"]
                    }
                    self.broker.publish('bs.alerts', payload)
                    
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
            "Temp": self.sensorTemp.temperatura_changed
        }
    