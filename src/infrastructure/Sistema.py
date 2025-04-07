from src.domain.entities.SensorTemperaturaEntitie import SensorTemperaturaEntitie
import threading
import time
import random

class Sistema:
    def __init__(self):
        self.sensorTemp = SensorTemperaturaEntitie()
        self.running = False
        
        # Iniciar el hilo para simular cambios de temperatura
        self.thread = threading.Thread(target=self.simular_cambios_temperatura, daemon=True)
        self.thread.start()

    def leerTemperaturas(self):
        print(f"Sensor de temperatura su temperatura minima es: {self.sensorTemp.TEMPERATURA_MINIMA}")
        print(f"Temperatura actual: {self.sensorTemp.temperatura}°C")

    def getSignals(self):
        return {
            "Temp": self.sensorTemp.temperatura_changed
        }
    
    def simular_cambios_temperatura(self):
        """
        Función que se ejecuta en un hilo separado y actualiza la temperatura
        con valores aleatorios cada segundo.
        """
        self.running = True
        
        # Valor inicial de temperatura (en un rango razonable)
        temperatura_actual = random.randint(45, 80)
        self.sensorTemp.update_temperature(temperatura_actual)
        
        while self.running:
            try:
                # Calcular una variación aleatoria de temperatura
                variacion = random.uniform(-2.0, 2.0)
                nueva_temperatura = int(temperatura_actual + variacion)
                
                # Asegurar que la temperatura tenga variaciones pero se mantenga en un rango realista
                nueva_temperatura = max(30, min(90, nueva_temperatura))
                
                # Actualizar el sensor de temperatura (esto emitirá la señal)
                self.sensorTemp.update_temperature(nueva_temperatura)
                temperatura_actual = nueva_temperatura
                
                # Esperar un segundo antes de la próxima actualización
                time.sleep(1)
            except Exception as e:
                print(f"Error en la simulación de temperatura: {str(e)}")
                time.sleep(1)  # En caso de error, esperar antes de reintentar
    
    def detener_simulacion(self):
        """Detiene la simulación de cambios de temperatura"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=2)  # Esperar hasta 2 segundos a que el hilo termine