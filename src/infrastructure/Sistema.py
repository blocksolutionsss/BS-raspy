from src.domain.entities.SensorTemperaturaEntitie import SensorTemperaturaEntitie
import threading
import time
import random
from ..domain.entities.BrokerEntitie import BrokerEntitie

class Sistema:
    def __init__(self):
        self.sensorTemp = SensorTemperaturaEntitie()
        self.running = False
        self.broker = BrokerEntitie()
        
        
        # Iniciar el hilo para simular cambios de temperatura
        self.thread_Temperatura = threading.Thread(target=self.leerTemperatura, daemon=True)
        self.thread_Temperatura.start()

    def leerTemperatura(self):
        """Simula la lectura de temperatura"""
        self.running = True
        while self.running:
            # Simular un cambio de temperatura aleatorio
            newTemp = random.randint(0, 100)
            self.sensorTemp.update_temperature(newTemp)
            # Publicar la nueva temperatura en el broker
            self.broker.publish("temperatura", {"temperatura": newTemp})
            time.sleep(1)

    def getSignals(self):
        return {
            "Temp": self.sensorTemp.temperatura_changed
        }
    
    def detener_simulacion(self):
        """Detiene la simulación de cambios de temperatura"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=2)  # Esperar hasta 2 segundos a que el hilo termine