import asyncio
import websockets
import pika
import socketio
import json
import time
import sqlite3  # Base de datos SQLite
from datetime import datetime
import threading  # Importar para manejar un hilo separado
import serial

# Configura el puerto serial y la velocidad (aseg�rate de usar el puerto correcto)
port = '/dev/ttyUSB0'  # Ajusta este valor al puerto correspondiente
baud_rate = 115200

# -------- Par�metros para monitoreo de temperatura y humedad -------------------
ESP32_IP = "192.168.43.21"
range_tempeture_max = 75
range_tempeture_min = 50
range_humidity_max = 30
range_humidity_min = 15



# Variables globales
esp32_connected = False
pending_messages = []
previous_monitoring = None










try:
    # Abre la conexi�n serial
    ser = serial.Serial(port, baud_rate, timeout=1)
    print("Esperando datos de la ESP32...")

    while True:
        # Lee los datos enviados por la ESP32
        data = ser.readline().decode('utf-8').strip()
        if data:
            print(f"Mensaje recibido: {data}")
            
            # Detecta cuando la ESP32 env�a que est� conectada
            if "Conectado a WiFi" in data:
                print("La ESP32 se conect� a internet")
            elif "No conectado a WiFi" in data:
                print("La ESP32 no est� conectada a internet")

except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
except KeyboardInterrupt:
    print("Finalizando...")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()








# ------- Configuraci�n de RabbitMQ ------------------------------------------------
rabbit_settings = {
    'protocol': 'amqp',
    'hostname': '54.163.129.164',
    'port': 5672,
    'username': 'blocksolutions-rasp',
    'password': 'leedpees'
}

credentials = pika.PlainCredentials(rabbit_settings['username'], rabbit_settings['password'])
parameters = pika.ConnectionParameters(
    host=rabbit_settings['hostname'],
    port=rabbit_settings['port'],
    credentials=credentials
)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

exchange = 'amq.topic'
channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)

print("Conectado a RabbitMQ")

# ------- SocketIO y WebSocket Client -------------------------------------------
sio = socketio.Client(reconnection=True, reconnection_attempts=20, reconnection_delay=2)
monitoring = False  # Variable global que controla el monitoreo
terminate_process = False
current_log_id = None
device = "device10"

# Eventos SocketIO
@sio.event
def connect():
    print("Conectado al servidor")

@sio.event
def disconnect():
    print("Desconectado del servidor")

@sio.event
def handle_event(event, data):
    print(f"Evento recibido: {event}")
    print(f"Datos: {data}")


@sio.event
def message(data):
    print(f"Mensaje recibido: {data}")


# Evento que activa o desactiva el monitoreo
@sio.on('power-control')
def handle_trigger(data):
    global monitoring
    monitoring = data['pause']

    if monitoring:
        print("Monitoreo activado")
    else:
        print("Monitoreo pausado")
        monitoring == False
        
@sio.on('terminate')
def handle_terminate(data):
    global terminate_process
    terminate_process = data['terminate']

# ----------------- BASE DE DATOS -------------------------------------------
def setup_database():
    conn = sqlite3.connect('deshidratador.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT,
            temperature REAL,
            humidity REAL,
            gas REAL,
            weight1 REAL,
            weight2 REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            "status" TEXT DEFAULT 'activated',  -- Estado: 'activated', 'paused', 'completed'
            duration REAL DEFAULT 0.0    
        )
    ''')
    
    # Crear tabla para registrar tiempos de deshidrataci�n
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dehydration_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT,
            start_time DATETIME,
            end_time DATETIME,
            estimated_duration REAL,
            "status" TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            value REAL,
            description TEXT,
            priority TEXT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            log_id INTEGER,
            FOREIGN KEY (log_id) REFERENCES dehydration_logs(id)
        )
    ''')

    conn.commit()
    conn.close()






async def handle_monitoring_update(monitoring, websocket):
    global previous_monitoring, esp32_connected, pending_messages

    # Verificar si el estado de monitoring ha cambiado
    if monitoring != previous_monitoring:
        message = {"monitoring": monitoring}
        print(f"Estado de monitoring ha cambiado: {message}")
        
        # Si el ESP32 est� conectado, enviamos el mensaje inmediatamente
        if esp32_connected:
            await websocket.send(json.dumps(message))
            print(f"Mensaje enviado al ESP32: {message}")
        else:
            # Si el ESP32 no est� conectado, lo almacenamos en la cola de pendientes
            pending_messages.append(message)
        
        # Actualizar previous_monitoring para evitar enviar el mismo mensaje
        previous_monitoring = monitoring







#Funcion para manejar la conexion WebSocket del ESP32
async def handle_esp32_connection(websocket, path):
    global monitoring, terminate_process, current_log_id, esp32_connected
    conn = sqlite3.connect('deshidratador.db')
    cursor = conn.cursor()

    client_ip = websocket.remote_address[0]
    print(f"Conexion desde: {client_ip}")
    if client_ip != "192.168.43.21":  # Asegarate de que sea el ESP32
        print(f"Conexion denegada desde {client_ip}")
        await websocket.close()
        return

    print("ESP32 conectado")
    esp32_connected = True  # El ESP32 se conecta


    try:
        await handle_monitoring_update(monitoring, websocket)

        while monitoring:
            message = await websocket.recv()
            try:
                # Parsear el mensaje recibido como JSON
                data = json.loads(message)
                if data.get("alert"):
                    #print(f'Data de alertas: {data}')
                    if "humidity" in data:
                        # Si la humedad excede el límite, se envía una alerta
                        humedad = data["humidity"]
                        if humedad < range_humidity_min:
                            prioridad = 'Baja' 
                            description = "debajo"
                        elif humedad > range_humidity_max:
                            prioridad = 'Alta'  
                            description = "encima"
                        payload = {
                            "device": device,
                            "notification":{
                                    'type': 'Humedad',
                                    'value': humedad,
                                    'range': "15-30",  # Rango de humedad
                                    'description': f'Humedad por {description} del rango',
                                    'priority': prioridad,  # Prioridad de la alerta
                                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                        }
                        save_notification(
                            payload["notification"]['type'],
                            humedad,
                            payload["notification"]['description'],
                            payload["notification"]['priority'],
                            current_log_id  # Usamos el log_id del historial activo
                        )
                        send_notification('bs.notifications', payload)

                    if "temperature" in data:
                        # Si la temperatura excede el límite, se envía una alerta
                        temperatura = data["temperature"]
                        if temperatura < range_tempeture_min:
                            prioridad = 'Baja' 
                            description = "debajo"
                        elif temperatura > range_tempeture_max:
                            prioridad = 'Alta'  
                            description = "encima"
                        payload = {
                            "device": device,
                            "notification":{
                                'type': 'Temperatura',
                                'value': temperatura,
                                'range': "50-75",  # Rango de temperatura
                                'description': f'Temperatura por {description} de rango',
                                'priority': prioridad,
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            }
                        }
                        save_notification(
                            payload["notification"]['type'],
                            payload["notification"]['value'],
                            payload["notification"]['description'],
                            payload["notification"]['priority'],
                            current_log_id  # Usamos el log_id del historial activo
                        )
                        send_notification('bs.notifications', payload)

                    if "flyClean" in data:
                        # Si el aire no está limpio, se envía una alerta
                        flyclean = data["flyClean"]
                        inverted_flyclean = 100 - flyclean
                        if inverted_flyclean >= 65:
                            prioridad = 'Baja'
                            descripcion = "Aire limnotificationspio"
                        else:
                            prioridad = 'Alta'  # Prioridad baja si el aire no es puro
                            descripcion = "Aire no puro"
                        payload = {
                            "device": device,
                            "notification":{
                                'type': 'Calidad de aire',
                                'value': inverted_flyclean,
                                'range': f"65% - 100%",  # Rango de calidad del aire (por ejemplo, 0 es limpio)
                                'description': descripcion,
                                'priority': prioridad,
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                            }
                        }
                        save_notification(
                            payload["notification"]['type'],
                            payload["notification"]['value'],
                            payload["notification"]['description'],
                            payload["notification"]['priority'],
                            current_log_id  # Usamos el log_id del historial activo
                        )
                        send_notification('bs.notifications', payload)

                    if "weight1" in data:
                        # Si el peso cambia significativamente, se envía una alerta
                        peso = data["weight1"]
                        payload = {
                            "device": device,
                            "notification":{
                                'type': 'Peso parrilla 1',
                                'value': peso,
                                'description': 'El peso cambio',
                                'priority': 'Bajo',  # Puedes ajustar la prioridad aquí
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            }
                        }
                        save_notification(
                            payload["notification"]['type'],
                            payload["notification"]['value'],
                            payload["notification"]['description'],
                            payload["notification"]['priority'],
                            current_log_id  # Usamos el log_id del historial activo
                        )
                        send_notification('bs.notifications', payload)
                    
                    if "weight2" in data:
                        # Si el peso cambia significativamente, se envía una alerta
                        peso = data["weight2"]
                        payload = {
                            "device": device,
                            "notification":{
                                'type': 'Peso parrilla 2',
                                'value': peso,
                                'description': 'El peso cambio',
                                'priority': 'Bajo',  # Puedes ajustar la prioridad aquí
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            }
                        }
                        save_notification(
                            payload["notification"]['type'],
                            payload["notification"]['value'],
                            payload["notification"]['description'],
                            payload["notification"]['priority'],
                            current_log_id  # Usamos el log_id del historial activo
                        )
                        send_notification('bs.notifications', payload)
                        
                    if "complete" in data:
                        # Si el peso cambia significativamente, se envía una alerta
                        status = data["complete"]
                        payload = {
                            "device": device,
                            "notification":{
                                'type': 'Estado',
                                'value': status,
                                'description': 'Deshidratación completada',
                                'priority': 'Bajo',  # Puedes ajustar la prioridad aquí
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            }# Listas globales para almacenar valores de temperatura y humedad
                        }
                        save_notification(
                            payload["notification"]['type'],
                            payload["notification"]['value'],
                            payload["notification"]['description'],
                            payload["notification"]['priority'],
                            current_log_id  # Usamos el log_id del historial activo
                        )
                        send_notification('bs.notifications', payload)
                else:
                    if "History" in data:
                        if monitoring:
                            if terminate_process:
                                reset_all()
 
                                # Terminar el historial actual y crear uno nuevo
                                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                                # Primero, actualizamos el historial actual si existe
                                if current_log_id:
                                    cursor.execute('''
                                        UPDATE dehydration_logs
                                        SET end_time = ?, status = ?
                                        WHERE id = ?
                                    ''', (timestamp, 'Completed', current_log_id))

                                # Crear un nuevo historial de deshidratacion
                                cursor.execute('''
                                    INSERT INTO dehydration_logs (device, start_time, status)
                                    VALUES (?, ?, ?)
                                ''', (device, timestamp, 'In Progress'))
                                current_log_id = cursor.lastrowid  # Establecer el nuevo log ID
                                terminate_process = False  # Resetear terminate despues de crear un nuevo historial

                                # Agregar alerta vinculada al nuevo historial
                            else:
                                temperature = data["temperatures"],
                                humidity = data["humidities"]
                                gas = data["gas"]
                                weight1 = data["weight1"],
                                weight2 = data["weight2"]
                                payload = {
                                    "device": device,
                                    "data": {
                                        "temperature": temperature,
                                        "humiditie": humidity,
                                        "gas": gas,
                                        "weight-1": weight1,
                                        "weight-2": weight2
                                    },
                                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }

                                save_historical_data(device, 
                                    payload["data"]["temperatures"],
                                    payload["data"]["humidities"],
                                    payload["data"]["gas"],
                                    payload["data"]["weight1"],
                                    payload["data"]["weight2"]
                                )

                                channel.basic_publish(
                                    exchange=exchange,
                                    routing_key="bs.history",
                                    body=json.dumps(payload)
                                )
                                print(f"Datos históricos enviados: {data['History']}")
                    else:
                        print("No se ha recibido una alerta ni datos históricos.")
            except ValueError:
                print("Error al parsear el mensaje. Asegurate de que el formato sea correcto.")
    except websockets.exceptions.ConnectionClosed:
        print("Conexion cerrada con ESP32")
        esp32_connected = False  # El ESP32 se desconect�
# ------- Funcion principal que coordina todo ----------------------------------
async def main():
    # Iniciar el hilo para Socket.IO
    threading.Thread(target=start_socketio).start()

    # Iniciar el servidor WebSocket
    await start_websocket_server()

# ------- Conexion Socket.IO -----------------------------------------------------
# Funcion para conectar a Socket.IO en un hilo separado
def start_socketio():
    try:
        print("Intentando conectar a Socket.IO...")
        sio.connect('http://54.236.151.211:3000')
        print("Conexion a Socket.IO establecida.")
    except Exception as e:
        print("No se pudo conectar a Socket.IO:", e)
    sio.wait()  # Mantener Socket.IO en espera de eventos

# ------- Servidor WebSocket para ESP32 ---------------------------------------
async def start_websocket_server():
    server = await websockets.serve(handle_esp32_connection, "0.0.0.0", 8080)
    print("Servidor WebSocket iniciado en ws://0.0.0.0:8080")
    await server.wait_closed()

# ------- Ejecutar el codigo asincronico ---------------------------------------
if __name__ == '__main__':
    setup_database()
    asyncio.run(main())