import time
import datetime
import sqlite3
from datetime import datetime
import json
import uuid

class SQLite3Entitie:
    def __init__(self, db_path='deshidratador.db'):
        self.db_path = db_path
        self.setup_database()
        self.initialize_device()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def setup_database(self):
        """Configura la estructura de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla de dispositivos principal
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                automatization BOOLEAN,
                temperature REAL,
                pre_set TEXT,
                humidity REAL,
                weight REAL,
                humidity_actual REAL,
                temperature_actual REAL,
                hours_actual INTEGER,
                minute_actual INTEGER,
                airPurity REAL,
                hours INTEGER,
                minutes INTEGER,
                pause BOOLEAN,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Historial de sesiones de deshidratación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS histories (
                id TEXT PRIMARY KEY,
                device_id TEXT,
                fruit TEXT,
                automatic BOOLEAN,
                hours INTEGER,
                minutes INTEGER,
                date DATETIME,
                FOREIGN KEY (device_id) REFERENCES devices(id)
            )
        ''')

        # Lecturas de temperatura para cada historial
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temperature_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history_id TEXT,
                temperature REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (history_id) REFERENCES histories(id)
            )
        ''')

        # Lecturas de humedad para cada historial
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS humidity_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history_id TEXT,
                humidity REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (history_id) REFERENCES histories(id)
            )
        ''')

        # Lecturas de peso para cada historial
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history_id TEXT,
                weight REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (history_id) REFERENCES histories(id)
            )
        ''')
        
        # Alertas y notificaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history_id TEXT,
                description TEXT,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                priority INTEGER,
                type TEXT,
                value REAL,
                FOREIGN KEY (history_id) REFERENCES histories(id)
            )
        ''')

        conn.commit()
        conn.close()
        print("Base de datos y tablas creadas exitosamente.")
    
    def initialize_device(self):
        """Inicializa el dispositivo si no existe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe el dispositivo
        cursor.execute('SELECT COUNT(*) FROM devices WHERE id = ?', ('device10',))
        device_exists = cursor.fetchone()[0] > 0
        
        if not device_exists:
            # Crear el dispositivo con valores por defecto
            cursor.execute('''
                INSERT INTO devices 
                (id, automatization, temperature, pre_set, humidity, weight, 
                humidity_actual, temperature_actual, hours_actual, minute_actual,
                airPurity, hours, minutes, pause, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'device10',  # ID fijo
                False,       # automatization
                0,           # temperature
                "1",         # pre_set
                0,           # humidity
                0,           # weight
                0,           # humidity_actual
                0,           # temperature_actual
                0,           # hours_actual
                0,           # minute_actual
                0,           # airPurity
                0,           # hours
                0,           # minutes
                True,        # pause
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # last_updated
            ))
            
            # Crear una historia vacía inicial
            history_id = "1"  # ID fijo para la primera historia
            
            cursor.execute('''
                INSERT INTO histories
                (id, device_id, fruit, automatic, hours, minutes, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                history_id,
                'device10',
                "",          # fruit
                False,       # automatic
                0,           # hours
                0,           # minutes
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # date
            ))
            
            print("Dispositivo inicializado con una historia vacía")
            
        conn.commit()
        conn.close()
    
    def update_device(self, data):
        """Actualiza los datos del dispositivo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Preparar los campos a actualizar
        fields = []
        values = []
        
        # Verificar cada campo posible y agregarlo si existe en data
        possible_fields = [
            'automatization', 'temperature', 'pre_set', 'humidity', 'weight',
            'humidity_actual', 'temperature_actual', 'hours_actual', 'minute_actual',
            'airPurity', 'hours', 'minutes', 'pause'
        ]
        
        for field in possible_fields:
            if field in data:
                fields.append(f"{field} = ?")
                values.append(data[field])
        
        # Agregar timestamp de última actualización
        fields.append("last_updated = ?")
        values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Construir la consulta SQL
        query = f"UPDATE devices SET {', '.join(fields)} WHERE id = 'device10'"
        
        # Ejecutar la consulta
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        print("Dispositivo actualizado correctamente")
    
    def add_temperature_reading(self, data):
        """Agrega una lectura de temperatura a la última historia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener el ID de la última historia
        cursor.execute('SELECT id FROM histories WHERE device_id = "device10" ORDER BY date DESC LIMIT 1')
        history_id_result = cursor.fetchone()
        
        if not history_id_result:
            conn.close()
            print("No se encontró historia para agregar temperatura")
            return False
        
        history_id = history_id_result[0]
        temperature = data.get('temperature', 0)
        
        # Insertar la lectura
        cursor.execute('''
            INSERT INTO temperature_readings (history_id, temperature)
            VALUES (?, ?)
        ''', (history_id, temperature))
        
        conn.commit()
        conn.close()
        
        print(f"Lectura de temperatura {temperature} agregada a historia {history_id}")
        return True
    
    def add_humidity_reading(self, data):
        """Agrega una lectura de humedad a la última historia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener el ID de la última historia
        cursor.execute('SELECT id FROM histories WHERE device_id = "device10" ORDER BY date DESC LIMIT 1')
        history_id_result = cursor.fetchone()
        
        if not history_id_result:
            conn.close()
            print("No se encontró historia para agregar humedad")
            return False
        
        history_id = history_id_result[0]
        humidity = data.get('humidity', 0)
        
        # Insertar la lectura
        cursor.execute('''
            INSERT INTO humidity_readings (history_id, humidity)
            VALUES (?, ?)
        ''', (history_id, humidity))
        
        conn.commit()
        conn.close()
        
        print(f"Lectura de humedad {humidity} agregada a historia {history_id}")
        return True
    
    def add_weight_reading(self, data):
        """Agrega una lectura de peso a la última historia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener el ID de la última historia
        cursor.execute('SELECT id FROM histories WHERE device_id = "device10" ORDER BY date DESC LIMIT 1')
        history_id_result = cursor.fetchone()
        
        if not history_id_result:
            conn.close()
            print("No se encontró historia para agregar peso")
            return False
        
        history_id = history_id_result[0]
        weight = data.get('weight', 0)
        
        # Insertar la lectura
        cursor.execute('''
            INSERT INTO weight_readings (history_id, weight)
            VALUES (?, ?)
        ''', (history_id, weight))
        
        conn.commit()
        conn.close()
        
        print(f"Lectura de peso {weight} agregada a historia {history_id}")
        return True
    
    def add_alert(self, data):
        """Agrega una alerta a la última historia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener el ID de la última historia
        cursor.execute('SELECT id FROM histories WHERE device_id = "device10" ORDER BY date DESC LIMIT 1')
        history_id_result = cursor.fetchone()
        
        if not history_id_result:
            conn.close()
            print("No se encontró historia para agregar alerta")
            return False
        
        history_id = history_id_result[0]
        
        # Obtener datos de la alerta
        description = data.get('description', '')
        priority = data.get('priority', 0)
        alert_type = data.get('type', '')
        value = data.get('value', 0)
        date = data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Insertar la alerta
        cursor.execute('''
            INSERT INTO alerts (history_id, description, date, priority, type, value)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (history_id, description, date, priority, alert_type, value))
        
        alert_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"Alerta '{description}' agregada con ID {alert_id}")
        return alert_id
    
    def update_history(self, data):
        """Actualiza la última historia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener el ID de la última historia
        cursor.execute('SELECT id FROM histories WHERE device_id = "device10" ORDER BY date DESC LIMIT 1')
        history_id_result = cursor.fetchone()
        
        if not history_id_result:
            conn.close()
            print("No se encontró historia para actualizar")
            return False
        
        history_id = history_id_result[0]
        
        # Preparar los campos a actualizar
        fields = []
        values = []
        
        # Verificar cada campo posible y agregarlo si existe en data
        possible_fields = ['fruit', 'automatic', 'hours', 'minutes']
        
        for field in possible_fields:
            if field in data:
                fields.append(f"{field} = ?")
                values.append(data[field])
        
        # Si hay campos para actualizar
        if fields:
            # Construir la consulta SQL
            query = f"UPDATE histories SET {', '.join(fields)} WHERE id = ?"
            values.append(history_id)
            
            # Ejecutar la consulta
            cursor.execute(query, values)
            
            conn.commit()
            print(f"Historia {history_id} actualizada correctamente")
        
        conn.close()
        return True
    
    def create_new_history(self, data=None):
        """Crea una nueva historia para el dispositivo"""
        if data is None:
            data = {}
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Generar ID para la nueva historia
        cursor.execute('SELECT COUNT(*) FROM histories')
        count = cursor.fetchone()[0]
        new_id = str(count + 1)
        
        # Obtener datos o usar valores por defecto
        fruit = data.get('fruit', '')
        automatic = data.get('automatic', False)
        hours = data.get('hours', 0)
        minutes = data.get('minutes', 0)
        date = data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Insertar nueva historia
        cursor.execute('''
            INSERT INTO histories (id, device_id, fruit, automatic, hours, minutes, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (new_id, 'device10', fruit, automatic, hours, minutes, date))
        
        conn.commit()
        conn.close()
        
        print(f"Nueva historia creada con ID {new_id}")
        return new_id
    
    def get_device(self):
        """Obtiene todos los datos del dispositivo incluyendo sus historias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener datos del dispositivo
        cursor.execute('SELECT * FROM devices WHERE id = "device10"')
        device_row = cursor.fetchone()
        
        if not device_row:
            conn.close()
            print("No se encontró el dispositivo")
            return None
        
        # Obtener nombres de columnas del dispositivo
        device_columns = [description[0] for description in cursor.description]
        device_data = dict(zip(device_columns, device_row))
        
        # Obtener historiales del dispositivo
        cursor.execute('SELECT id FROM histories WHERE device_id = "device10" ORDER BY date DESC')
        history_ids = cursor.fetchall()
        
        histories = []
        for (history_id,) in history_ids:
            # Obtener datos del historial
            cursor.execute('SELECT * FROM histories WHERE id = ?', (history_id,))
            history_row = cursor.fetchone()
            history_columns = [description[0] for description in cursor.description]
            history_data = dict(zip(history_columns, history_row))
            
            # Obtener temperaturas
            cursor.execute('SELECT temperature FROM temperature_readings WHERE history_id = ? ORDER BY timestamp', (history_id,))
            temperatures = [row[0] for row in cursor.fetchall()]
            
            # Obtener humedades
            cursor.execute('SELECT humidity FROM humidity_readings WHERE history_id = ? ORDER BY timestamp', (history_id,))
            humidities = [row[0] for row in cursor.fetchall()]
            
            # Obtener pesos
            cursor.execute('SELECT weight FROM weight_readings WHERE history_id = ? ORDER BY timestamp', (history_id,))
            weights = [row[0] for row in cursor.fetchall()]
            
            # Obtener alertas
            cursor.execute('SELECT * FROM alerts WHERE history_id = ? ORDER BY date', (history_id,))
            alert_rows = cursor.fetchall()
            alert_columns = [description[0] for description in cursor.description]
            
            alerts = []
            for alert_row in alert_rows:
                alert_data = dict(zip(alert_columns, alert_row))
                alert_formatted = {
                    "id": str(alert_data.get("id")),
                    "description": alert_data.get("description", ""),
                    "date": alert_data.get("date", ""),
                    "priority": alert_data.get("priority", 0),
                }
                alerts.append(alert_formatted)
            
            # Construir historial completo
            complete_history = {
                "id": history_data.get("id"),
                "temperatures": temperatures,
                "humidities": humidities,
                "weights": weights,
                "fruit": history_data.get("fruit", ""),
                "automatic": bool(history_data.get("automatic", False)),
                "hours": history_data.get("hours", 0),
                "minutes": history_data.get("minutes", 0),
                "date": history_data.get("date", ""),
                "alerts": alerts
            }
            
            histories.append(complete_history)
        
        # Si no hay historias, crear una vacía
        if not histories:
            new_history_id = self.create_new_history()
            histories = [{
                "id": new_history_id,
                "temperatures": [],
                "humidities": [],
                "weights": [],
                "fruit": "",
                "automatic": False,
                "hours": 0,
                "minutes": 0,
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "alerts": []
            }]
        
        # Construir dispositivo completo
        complete_device = {
            "id": device_data.get("id"),
            "automatization": bool(device_data.get("automatization", False)),
            "temperature": device_data.get("temperature", 0),
            "pre_set": device_data.get("pre_set", "1"),
            "humidity": device_data.get("humidity", 0),
            "weight": device_data.get("weight", 0),
            "humidity_actual": device_data.get("humidity_actual", 0),
            "temperature_actual": device_data.get("temperature_actual", 0),
            "hours_actual": device_data.get("hours_actual", 0),
            "minute_actual": device_data.get("minute_actual", 0),
            "airPurity": device_data.get("airPurity", 0),
            "hours": device_data.get("hours", 0),
            "minutes": device_data.get("minutes", 0),
            "pause": bool(device_data.get("pause", True)),
            "histories": histories
        }
        
        conn.close()
        return complete_device