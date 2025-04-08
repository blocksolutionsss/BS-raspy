import socketio
import threading
import time
from .config import SOCKETIO_HOST
from .share_states import set_monitoring, set_terminate,reset_elapsed_time, increment_elapsed_time, toggle_pause_time
from .esp32 import comunicacion_serial

# Crear una instancia de Socket.IO
sio = socketio.Client()

# Flag para asegurar que solo haya un intento de conexi�n
is_connecting = False

# Evento de conexi�n
@sio.event
def connect():
    global is_connecting
    is_connecting = False
    print("Conexion establecida con el servidor Socket.IO")

# Evento de desconexi�n
@sio.event
def disconnect():
    global is_connecting
    print("Desconectado del servidor Socket.IO")
    is_connecting = False  # Restablecer el flag cuando se desconecta


@sio.on('power-control')
def handle_trigger(data):
    monitoring = data['pause']
    if monitoring:
        set_monitoring(False) 
        print("Monitoreo pausado")
        toggle_pause_time()
        activar_puerto = False
        comunicacion_serial(activar_puerto)
    else:
        set_monitoring(True) 
        print("Monitoreo activado")
        #increment_elapsed_time()
        activar_puerto = True
        comunicacion_serial(activar_puerto)

@sio.on('process-control')
def handle_terminate(data):
    global terminate_process
    terminate_process = data['process']
    print("Monitoreo terminado")
    set_monitoring(False)
    set_terminate(True)
    activar_puerto = False
    comunicacion_serial(activar_puerto)
    reset_elapsed_time()    

def send_data_to_socket(message):
    print(f"Enviando mensaje al servidor: {message}")
    sio.emit('message', message)

# Funci�n para gestionar la conexi�n y la reconexi�n
def handle_socketio_connection():
    global is_connecting
    while True:
        try:
            # Conectar si no estamos conectados y no estamos en el proceso de conexi�n
            if not sio.connected and not is_connecting:
                is_connecting = True
                print("Intentando conectar con el servidor Socket.IO...")
                sio.connect(SOCKETIO_HOST)
            while sio.connected:
                # Mantener la conexi�n activa
                time.sleep(1)

        except Exception as e:
            print(f"Error en la conexion de Socket.IO: {e}")

        # Si se pierde la conexi�n, restablecer el estado de conexi�n
        if not sio.connected:
            print("Conexion perdida. Intentando reconectar...")
            is_connecting = False
        time.sleep(5)  # Esperar 5 segundos antes de volver a intentar

# Funci�n para iniciar el hilo de conexi�n y reconexi�n en un solo hilo
def start_socketio_thread():
    socketio_thread = threading.Thread(target=handle_socketio_connection)
    socketio_thread.daemon = True  # El hilo se cierra cuando el programa principal termina
    socketio_thread.start()
    print("Conexion y reconexion de Socket.IO gestionados en un solo hilo.")
