import socketio
import threading
import time
from src.domain.entities.ESP32Entitie import ESP32Entitie

class SocketIOEntitie:
    SOCKETIO_HOST = 'http://192.168.137.254:3000'
    DEVICE = "device10"
    def __init__(self, esp32, device_data):
        self.esp32: ESP32Entitie = esp32
        self.device_data = device_data
        self.sio = socketio.Client()
        self.is_connecting = False
        self._setup_events()
        
        thread = threading.Thread(target=self._connect_loop, daemon=True)
        thread.start()
        print("Conexión y reconexión de Socket.IO gestionadas en un solo hilo.")
    
    def _setup_events(self):
        @self.sio.event
        def connect():
            self.is_connecting = False
            print("Conexión establecida con el servidor Socket.IO")

        @self.sio.event
        def disconnect():
            print("Desconectado del servidor Socket.IO")
            self.is_connecting = False

        @self.sio.on('power-control')
        def handle_trigger(data):
            monitoring = data['pause']
            if monitoring:
                print("Monitoreo pausado")
                self.esp32.iniciar_monitoreo(self.device_data["temperature"], self.device_data["humidity"])
            else:
                print("Monitoreo activado")
                self.esp32.pausar_monitoreo()

        @self.sio.on('process-control')
        def handle_terminate(data):
            print("Monitoreo terminado")
            set_monitoring(False)
            set_terminate(True)
            comunicacion_serial(False)
            reset_elapsed_time()

    def send_data(self, message):
        print(f"Enviando mensaje al servidor: {message}")
        self.sio.emit('message', message)

    def _connect_loop(self):
        while True:
            try:
                if not self.sio.connected and not self.is_connecting:
                    self.is_connecting = True
                    print("Intentando conectar con el servidor Socket.IO...")
                    self.sio.connect(self.SOCKETIO_HOST)
                while self.sio.connected:
                    time.sleep(1)
            except Exception as e:
                print(f"Error en la conexión de Socket.IO: {e}")
            if not self.sio.connected:
                print("Conexión perdida. Intentando reconectar...")
                self.is_connecting = False
            time.sleep(5)

