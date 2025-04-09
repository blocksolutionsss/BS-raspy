from serial import Serial, SerialException
from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
import json
from time import sleep

@dataclass
class ESP32Entitie(QObject):
    # Definición de señales
    serial_data_changed = Signal(str)  # Señal que se emitirá cuando cambien los datos seriales
    
    def __init__(self):
        super().__init__()
        self.puerto = '/dev/ttyACM0'  # Cambiar si es necesario
        self.velocidad = 115200       # Configura la misma velocidad que en la ESP32
        try:
            self.serial = Serial(self.puerto, self.velocidad, timeout=1)
            self.serial.flushInput()  # Limpiar el buffer de entrada al iniciar
            print(f"Conexión serial establecida en {self.puerto} a {self.velocidad} baudios")
        except SerialException as e:
            print(f"Error al inicializar puerto serial: {e}")
            self.serial = None
    
    def conectar(self):
        """Intenta establecer la conexión serial si no está activa"""
        if self.serial is None or not self.serial.is_open:
            try:
                self.serial = Serial(self.puerto, self.velocidad, timeout=1)
                self.serial.flushInput()
                print(f"Conexión serial restablecida en {self.puerto}")
                return True
            except SerialException as e:
                print(f"Error al conectar puerto serial: {e}")
                self.serial = None
                return False
        return True

    def update_serial_data(self, newSerial_data: str):
        """Emite la señal con nuevos datos seriales"""
        if newSerial_data:
            self.serial_data_changed.emit(newSerial_data)

    def iniciar_monitoreo(self, temperature, humidity):
        """Inicia el monitoreo enviando parámetros de temperatura y humedad"""
        if not self.conectar():
            return False
        
        try:
            data = {
                "event": "start",
                "sensor": {
                    "temperature": temperature,
                    "humidity": humidity
                }
            }

            message = json.dumps(data) + "\n"  # Agregar salto de linea para indicar fin del mensaje
            self.serial.write(message.encode())
            print(f"Enviado al ESP32: {data}")
            return True

        except SerialException as e:
            print(f"Error al acceder al puerto serial: {e}")
            return False
    
    def pausar_monitoreo(self):
        """Pausa el monitoreo enviando el comando de pausa"""
        if not self.conectar():
            return False
        
        try:
            data = {
                "event": "pause"
            }

            message = json.dumps(data) + "\n"  # Agregar salto de linea para indicar fin del mensaje
            self.serial.write(message.encode())
            print(f"Enviado al ESP32: {data}")
            return True

        except SerialException as e:
            print(f"Error al acceder al puerto serial: {e}")
            return False
            
    def reiniciar_esp32(self):
        """Maneja el reinicio del ESP32 a través de DTR y RTS"""
        if not self.conectar():
            return False
            
        try:
            # Apagar DTR y RTS para reiniciar el ESP32
            print("Reiniciando ESP32...")
            self.serial.setDTR(False)  # Desactivar DTR
            self.serial.setRTS(False)  # Desactivar RTS

            sleep(0.1)  # Esperar un momento

            # Volver a activar DTR y RTS
            self.serial.setDTR(True)  # Activar DTR
            self.serial.setRTS(True)  # Activar RTS
            return True
        except SerialException as e:
            print(f"Error al reiniciar ESP32: {e}")
            return False
    
    def enviar_comando(self, comando):
        """Envía un comando al ESP32"""
        if not self.conectar():
            return False
            
        try:
            if not isinstance(comando, bytes):
                comando = str(comando).encode('utf-8')
                if not comando.endswith(b'\n'):
                    comando += b'\n'
                    
            self.serial.write(comando)
            self.serial.flush()  # Asegura que se envíen todos los datos
            return True
        except SerialException as e:
            print(f"Error al enviar comando: {e}")
            return False
    
    def leer_respuesta(self, timeout=2.0):
        """Lee la respuesta del ESP32 con un timeout específico"""
        if not self.conectar():
            return "Error: No hay conexión serial"
            
        try:
            self.serial.timeout = timeout
            respuesta = self.serial.readline()
            if respuesta:
                return respuesta.decode('utf-8').strip()
            return ""
        except UnicodeDecodeError:
            return "Error: Datos no decodificables"
        except SerialException as e:
            print(f"Error al leer respuesta: {e}")
            return "Error: Excepción serial"
    
    def leer_multiples_lineas(self, num_lineas=5, timeout=2.0):
        """Lee múltiples líneas de respuesta del ESP32"""
        if not self.conectar():
            return ["Error: No hay conexión serial"]
            
        try:
            self.serial.timeout = timeout
            respuestas = []
            for _ in range(num_lineas):
                linea = self.serial.readline()
                if linea:  # Si recibimos datos
                    try:
                        texto = linea.decode('utf-8').strip()
                        if texto:  # Si la línea no está vacía
                            respuestas.append(texto)
                        else:
                            if not respuestas:  # Si no hemos recibido nada y esta línea está vacía
                                continue  # Intentamos leer otra línea
                            else:
                                break  # Si ya tenemos respuestas y esta línea está vacía, terminamos
                    except UnicodeDecodeError:
                        respuestas.append("Error: Datos no decodificables")
                else:
                    break  # Si no hay más datos para leer
                    
            return respuestas
        except SerialException as e:
            print(f"Error al leer múltiples líneas: {e}")
            return ["Error: Excepción serial"]
    
    def enviar_recibir(self, comando, timeout=2.0):
        """Envía un comando y espera una respuesta"""
        if self.enviar_comando(comando):
            return self.leer_respuesta(timeout)
        return "Error: No se pudo enviar el comando"
    
    def verificar_conexion(self):
        """Verifica si la conexión con el ESP32 está activa"""
        if not self.conectar():
            return False
            
        try:
            self.enviar_comando("PING")
            respuesta = self.leer_respuesta(timeout=1.0)
            return "PONG" in respuesta
        except Exception as e:
            print(f"Error al verificar conexión: {e}")
            return False
    
    def cerrar(self):
        """Cierra la conexión con el ESP32"""
        if hasattr(self, 'serial') and self.serial and self.serial.is_open:
            try:
                self.serial.close()
                print("Conexión serial cerrada")
            except SerialException as e:
                print(f"Error al cerrar la conexión: {e}")
    
    def __del__(self):
        """Destructor que asegura el cierre de la conexión"""
        self.cerrar()