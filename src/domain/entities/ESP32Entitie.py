from serial import Serial, SerialException
from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from json import dumps
from time import sleep

@dataclass
class ESP32Entitie(QObject):
    # Definición de señales
    serial_data_changed = Signal(str)  # Señal que se emitirá cuando cambie la calidad_Aire
    
    def __init__(self):
        super().__init__()
        self.puerto = '/dev/ttyACM0'  # Cambiar si es necesario
        self.velocidad = 115200       # Configura la misma velocidad que en la ESP32
        self.serial = Serial(self.puerto, self.velocidad)
        self.serial.flushInput()  # Limpiar el buffer de entrada al iniciar

    def update_serial_data(self, newSerial_data: str):
        self.serial_data_changed.emit(newSerial_data)

    def iniciar_monitoreo(self, temperature, humidity):
        try:
            print(f"Iniciando Monitorización")
            
            data = {
                "event": "start",
                "sensor": {
                    "temperature": temperature,
                    "humidity": humidity
                }
            }

            message = dumps(data) + "\n"  # Agregar salto de linea para indicar fin del mensaje

            self.serial.write(message.encode())
            print(f"Enviado al ESP32: {data}")

        except SerialException as e:
            print(f"Error al acceder al puerto serial: {e}")
    
    def pausar_monitoreo(self):
        try:
            print(f"Pausando Monitorización")
            
            data = {
                "event": "pause"
            }

            message = dumps(data) + "\n"  # Agregar salto de linea para indicar fin del mensaje

            self.serial.write(message.encode())
            print(f"Enviado al ESP32: {data}")

        except SerialException as e:
            print(f"Error al acceder al puerto serial: {e}")
            
    # Funcion que maneja el reinicio del ESP32 a traves de DTR y RTS
    def reiniciar_esp32(self):
        # Apagar DTR y RTS para reiniciar el ESP32
        print("Reiniciando ESP32...")
        self.serial.setDTR(False)  # Desactivar DTR
        self.serial.setRTS(False)  # Desactivar RTS

        sleep(0.1)  # Esperar un momento

        # Volver a activar DTR y RTS
        self.serial.setDTR(True)  # Activar DTR
        self.serial.setRTS(True)  # Activar RTS
    
    def enviar_comando(self, comando):
        """
        Envía un comando al ESP32
        """
        if not isinstance(comando, bytes):
            comando = str(comando).encode('utf-8') + b'\n'
        self.serial.write(comando)
        self.serial.flush()  # Asegura que se envíen todos los datos
    
    def leer_respuesta(self, timeout=2.0):
        """
        Lee la respuesta del ESP32 con un timeout específico
        """
        self.serial.timeout = timeout
        try:
            respuesta = self.serial.readline().decode('utf-8').strip()
            return respuesta
        except UnicodeDecodeError:
            return "Error: Datos no decodificables"
    
    def leer_multiples_lineas(self, num_lineas=5, timeout=2.0):
        """
        Lee múltiples líneas de respuesta del ESP32
        """
        self.serial.timeout = timeout
        respuestas = []
        for _ in range(num_lineas):
            try:
                linea = self.serial.readline().decode('utf-8').strip()
                if linea:  # Si la línea no está vacía
                    respuestas.append(linea)
                else:
                    break  # Si recibimos una línea vacía, terminamos
            except UnicodeDecodeError:
                respuestas.append("Error: Datos no decodificables")
        return respuestas
    
    def enviar_recibir(self, comando, timeout=2.0):
        """
        Envía un comando y espera una respuesta
        """
        self.enviar_comando(comando)
        return self.leer_respuesta(timeout)
    
    def verificar_conexion(self):
        """
        Verifica si la conexión con el ESP32 está activa
        """
        try:
            self.enviar_comando("PING")
            respuesta = self.leer_respuesta(timeout=1.0)
            return "PONG" in respuesta
        except Exception as e:
            print(f"Error al verificar conexión: {e}")
            return False
    
    def cerrar(self):
        """
        Cierra la conexión con el ESP32
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Conexión cerrada")
    
    def __del__(self):
        """
        Destructor que asegura el cierre de la conexión
        """
        self.cerrar()