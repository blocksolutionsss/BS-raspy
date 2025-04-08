import serial
import threading
import time
import json
import sqlite3
from datetime import datetime

from .rabbit import send_notification
from .share_states import get_monitoring, get_terminate,get_elapsed_time, start_counter, set_terminate
from .databaseLocal import save_historical_data

from front import app


range_tempeture_max = 75
range_tempeture_min = 50
range_humidity_max = 30
range_humidity_min = 15

device = "device10"

puerto = '/dev/ttyACM0'  # Cambiar si es necesario
velocidad = 115200       # Configura la misma velocidad que en la ESP32

prev_monitoring_value = None


last_humidity = None
last_tem = None
last_airPurity = None
last_weight1 = None
last_weight2 = None

last_humidity_r = None
last_tem_r = None
last_airPurity_r = None
last_weight1_r = None
last_weight2_r = None

last_values = {
    "temperature": None,
    "humidity": None,
    "airPurity": None,
    "weight1": None,
    "weight2": None,
    "hours": None,
    "minutes": None,
}

current_log_id = None

def reset_all():
    global current_log_id
    # Se restablece current_log_id y cualquier otra variable que necesite reiniciar
    current_log_id = None
    print("Se ha reiniciado todo.")


# Funci�n que maneja el reinicio del ESP32 a trav�s de DTR y RTS
def reiniciar_esp32():
    # Abrir el puerto serial donde est� conectado el ESP32
    ser = serial.Serial(puerto, velocidad, timeout=1)

    # Apagar DTR y RTS para reiniciar el ESP32
    print("Reiniciando ESP32...")
    ser.setDTR(False)  # Desactivar DTR
    ser.setRTS(False)  # Desactivar RTS

    time.sleep(0.1)  # Esperar un momento

    # Volver a activar DTR y RTS
    ser.setDTR(True)  # Activar DTR
    ser.setRTS(True)  # Activar RTS

    # Esperar un poco para que el ESP32 se reinicie completamente
    time.sleep(2)

    # Cerrar el puerto serial despu�s de reiniciar
    ser.close()

def comunicacion_serial(interruptor):
    try:
        ser = serial.Serial(puerto, velocidad, timeout=1)

        print(f"EL PUERTOOOOOOO {interruptor}")
        
        monitoring_value = get_monitoring()
        data = {
            "monitoring": interruptor
        }

        message = json.dumps(data) + "\n"  # Agregar salto de linea para indicar fin del mensaje

        ser.write(message.encode())
        print(f"Enviado al ESP32: {data}")

    except serial.SerialException as e:
        print(f"Error al acceder al puerto serial: {e}")
    finally:
        ser.close()

def comunicacion_serial_recibir():
    global current_log_id,last_humidity, last_tem, last_airPurity, last_weight1, last_weight2, last_humidity_r, last_tem_r, last_airPurity_r, last_weight1_r, last_weight2_r, last_values
    conn = sqlite3.connect('deshidratador.db')
    cursor = conn.cursor()
    start_counter()

    time.sleep(3)
    ser = None
    description = ""
    prioridad = "Normal"

    try:
        ser = serial.Serial(puerto, velocidad, timeout=1)
        time.sleep(2)  
        while True:
            if ser.in_waiting > 0:  # Si hay datos disponibles en el puerto
                try:
                    data = ser.readline().decode('utf-8').strip()  # Lee la l�nea de datos
                    if data:
                        print(f"ESP32: {data}")
                        app.actualizar_label_limite(data)
                        try:
                            data = json.loads(data)
                            {
                                "alert": {},
                                "real-time": {},
                                "End": {},
                            }
                            print(f"Datos deserializados: {data}")
                            if "alert" in data:
                                if "humidity" in data:                           
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
                                                'priority': prioridad, 
                                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            }
                                    }

                                    if last_humidity is None or humedad != last_humidity:
                                        last_humidity = humedad
                                        send_notification('bs.notifications', payload)
                                    else:
                                        print(f"Dato descartado. Dato recibido ({humedad})")                                

                                if "temperature" in data:
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
                                    if last_tem is None or temperatura != last_tem:
                                        last_tem = temperatura
                                        send_notification('bs.notifications', payload)
                                    else:
                                        print(f"Dato descartado. Dato recibido ({temperatura})")

                                if "flyClean" in data:
                                    airPurity = data["flyClean"]
                                    if airPurity >= 70:
                                        prioridad = 'Baja'
                                        descripcion = "Aire limpio"
                                    else:
                                        prioridad = 'Alta'  # Prioridad baja si el aire no es puro
                                        descripcion = "Aire no puro"
                                    payload = {
                                        "device": device,
                                        "notification":{
                                            'type': 'Calidad de aire',
                                            'value': airPurity,
                                            'range': f"65% - 100%",  # Rango de calidad del aire (por ejemplo, 0 es limpio)
                                            'description': descripcion,
                                            'priority': prioridad,
                                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                        }
                                    }
                                    if last_airPurity is None or airPurity != last_airPurity:
                                        last_airPurity = airPurity
                                        send_notification('bs.notifications', payload)
                                    else:
                                        print(f"Dato descartado. Dato recibido ({airPurity})")

                                if "weight1" in data:                                  
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
                                    if last_weight1 is None or peso != last_weight1:
                                        last_weight1 = peso
                                        send_notification('bs.notifications', payload)
                                    else:
                                        print(f"Dato descartado. Dato recibido ({peso})")
                                
                                if "weight2" in data:                                  
                                    peso2 = data["weight2"]
                                    payload = {
                                        "device": device,
                                        "notification":{
                                            'type': 'Peso parrilla 2',
                                            'value': peso2,
                                            'description': 'El peso cambio',
                                            'priority': 'Bajo',  # Puedes ajustar la prioridad aquí
                                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        }
                                    }
                                    if last_weight2 is None or peso2 != last_weight2:
                                        last_weight2 = peso2
                                        send_notification('bs.notifications', payload)
                                    else:
                                        print(f"Dato descartado. Dato recibido ({peso2})")
                                    
                                if "status" in data:
                                    # Si el peso cambia significativamente, se envía una alerta
                                    status = data["status"]
                                    payload = {
                                        "device": device,
                                        "notification":{
                                            'type': 'Estado',
                                            'value': status,
                                            'description': 'Deshidratación completada',
                                            'priority': 'Bajo',  # Puedes ajustar la prioridad aquí
                                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        }
                                    }
                                    send_notification('bs.notifications', payload)
                            elif "real-time" in data:
                                if "humidity" in data:                                  
                                    humidity = data["humidity"]
                                    payload = {
                                        "device": device,
                                        "humidity": humidity
                                    }
                                    if last_humidity_r is None or humidity != last_humidity_r:
                                        last_humidity_r = humidity
                                        send_notification('bs.real-time-humidity', payload)
                                        app.update_humidity(humidity)
                                    else:
                                        print(f"Dato descartado. Humedad recibida ({humidity})")
                                if "temperature" in data:
                                    temperature = data["temperature"]
                                    payload = {
                                        "device": device,
                                        "temperature": temperature
                                    }
                                    if last_tem_r is None or temperature != last_tem_r:
                                        last_tem_r = temperature
                                        send_notification('bs.real-time-temperature', payload)
                                        app.update_temperature(temperature)
                                    else:
                                        print(f"Dato descartado. Humedad recibida ({temperature})")
                                if "flyClean" in data:
                                    airPurity = data["flyClean"]
                                    payload = {
                                        "device": device,
                                        "airPurity": airPurity
                                    }
                                    if last_airPurity_r is None or airPurity != last_airPurity_r:
                                        last_airPurity_r = airPurity
                                        send_notification('bs.real-time-airPurity', payload)
                                        app.update_air_quality(airPurity)
                                    else:
                                        print(f"Dato descartado. Humedad recibida ({airPurity})")
                                if "weight1" in data:
                                    weight1 = data["weight1"]
                                    payload = {
                                        "device": device,
                                        "weight1": weight1
                                    }
                                    if last_weight1_r is None or weight1 != last_weight1_r:
                                        last_weight1_r = weight1
                                        send_notification('bs.real-time-weight1', payload)
                                        app.update_weight1(weight1)
                                    else:
                                        print(f"Dato descartado. Humedad recibida ({weight1})")
                                if "weight2" in data:
                                    weight2 = data["weight2"]
                                    payload = {
                                        "device": device,
                                        "weight2": weight2
                                    }
                                    if last_weight2_r is None or weight2 != last_weight2_r:
                                        last_weight2_r = weight2
                                        send_notification('bs.real-time-weight2', payload)
                                        app.update_weight2(weight2)
                                    else:
                                        print(f"Dato descartado. Humedad recibida ({weight2})")
                            elif "End" in data:
                                temperature = data["temperature"],
                                humidity = data["humidity"]
                                airPurity = data["flyClean"]
                                weight1 = data["weight1"],
                                weight2 = data["weight2"]
                                current_time = get_elapsed_time()
                                hours = current_time['hours']
                                minutes = current_time['minutes']
                                seconds = current_time['seconds']
                                payload = {
                                    "device": device,
                                    "data": {
                                        "status": "Completed",
                                        "humidity": humidity,
                                        "temperature": temperature,
                                        "airPurity": airPurity,
                                        "weight1": weight1,
                                        "weight2": weight2,
                                        "hours": hours,
                                        "minutes": minutes,
                                        "seconds": seconds
                                    },
                                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                send_notification("bs.history", payload)
                            else:
                                if "History" in data:
                                    monitoring = get_monitoring
                                    terminate = get_terminate
                                    if monitoring:
                                        if terminate:
                                            reset_all()
                                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            if current_log_id:
                                                cursor.execute('''
                                                    UPDATE dehydration_logs
                                                    SET end_time = ?, status = ?
                                                    WHERE id = ?
                                                ''', (timestamp, 'Completed', current_log_id))
                                            cursor.execute('''
                                                INSERT INTO dehydration_logs (device, start_time, status)
                                                VALUES (?, ?, ?)
                                            ''', (device, timestamp, 'In Progress'))
                                            current_log_id = cursor.lastrowid  # Establecer el nuevo log ID
                                            set_terminate(False)
                                        else:
                                            temperature = data["temperature"],
                                            humidity = data["humidity"]
                                            airPurity = data["flyClean"]
                                            weight1 = data["weight1"],
                                            weight2 = data["weight2"]
                                            current_time = get_elapsed_time()
                                            hours = current_time['hours']
                                            minutes = current_time['minutes']
                                            payload = {
                                                "humidity": humidity,
                                                "temperature": temperature,
                                                "airPurity": airPurity,
                                                "weight1": weight1,
                                                "weight2": weight2,
                                                "hours": hours,
                                                "minutes": minutes
                                            }

                                            for key, value in payload.items():
                                                if last_values[key] is None or last_values[key] != value:
                                                    last_values[key] = value

                                                    # Crear un payload especifico para el dato modificado
                                                    send_notification("bs.history", {
                                                        "device": device,
                                                        "data": {key: value},
                                                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                    })
                                                    save_historical_data(device, temperature, humidity, airPurity, weight1, weight2)
                                                else:
                                                    print(f"Dato descartado para {key}. Valor recibido: {value}")

                                            print(f"\nDatos históricos enviados\n")
                                else:
                                    print("No se ha recibido una alerta ni datos históricos.")
                        except json.JSONDecodeError:
                            pass
                except UnicodeDecodeError as e:
                    pass
                time.sleep(0.1)  # Evitar consumir demasiado CPU

    except serial.SerialException as e:
        print(f"Error al acceder al puerto serial: {e}")
    finally:
        if ser:  # Solo cierra 'ser' si se ha abierto correctamente
            ser.close()



def start_serial_esp32():
    reiniciar_esp32()

    hilo_comunicacion_recibo = threading.Thread(target=comunicacion_serial_recibir)
    hilo_comunicacion_recibo.daemon = True  # El hilo se cerraroo cuando el programa principal termine
    hilo_comunicacion_recibo.start()

    # El hilo principal puede seguir ejecutando otras tareas aqui...
    print("Hilo de comunicacion serial iniciado.")
