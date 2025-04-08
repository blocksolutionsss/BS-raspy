import time
import datetime
import sqlite3
from datetime import datetime

class SQLite3Entitie:
    def __init__(self, db_path='deshidratador.db'):
        self.db_path = db_path
        self.setup_database()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def setup_database(self):
        """Configura la estructura de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Crear tabla para almacenar datos históricos de los dispositivos
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
        
        # Crear tabla para registrar tiempos de deshidratación
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
        
        # Crear tabla para almacenar notificaciones
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
        print("Base de datos y tablas creadas exitosamente.")
    
    def save_historical_data(self, device, temperature, humidity, gas, weight1, weight2, status='activated', duration=0.0):
        """Guarda datos históricos en la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Registrar la hora de inicio
        start_time = time.time()
        
        cursor.execute('''
            INSERT INTO data_history (device, temperature, humidity, gas, weight1, weight2, status, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (device, temperature, humidity, gas, weight1, weight2, status, duration))
        
        conn.commit()
        conn.close()
        
        # Calcular la duración y actualizar el estado si es necesario
        end_time = time.time()
        duration = end_time - start_time  # Duración en segundos

        # Actualizar estado a 'completed' y duración
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE data_history
            SET status = ?, duration = ?
            WHERE device = ? AND status = 'activated'
        ''', ('completed', duration, device))
        conn.commit()
        conn.close()

        print("Datos históricos guardados en la base de datos con estado y duración.")
    
    def save_notification(self, notification_type, value, description, priority, log_id):
        """Guarda una notificación en la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notificaciones (type, value, description, priority, date, log_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (notification_type, value, description, priority, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), log_id))
        conn.commit()
        conn.close()
        print(f"Notificación '{description}' guardada para el historial con ID {log_id}.")
    
    def create_dehydration_log(self, device, estimated_duration=0.0):
        """Crea un nuevo registro de deshidratación y devuelve su ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO dehydration_logs (device, start_time, status, estimated_duration)
            VALUES (?, ?, ?, ?)
        ''', (device, start_time, 'In Progress', estimated_duration))
        
        # Obtener el ID del registro recién creado
        log_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"Nuevo registro de deshidratación creado con ID: {log_id}")
        return log_id
    
    def update_dehydration_log(self, log_id, status, end_time=None):
        """Actualiza un registro de deshidratación"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if end_time is None and status == 'Completed':
            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if end_time:
            cursor.execute('''
                UPDATE dehydration_logs
                SET status = ?, end_time = ?
                WHERE id = ?
            ''', (status, end_time, log_id))
        else:
            cursor.execute('''
                UPDATE dehydration_logs
                SET status = ?
                WHERE id = ?
            ''', (status, log_id))
        
        conn.commit()
        conn.close()
        
        print(f"Registro de deshidratación {log_id} actualizado a estado: {status}")
    
    def get_latest_data(self, device, limit=10):
        """Obtiene los datos más recientes para un dispositivo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM data_history
            WHERE device = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (device, limit))
        
        rows = cursor.fetchall()
        
        # Obtener nombres de columnas
        column_names = [description[0] for description in cursor.description]
        
        # Convertir a lista de diccionarios
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))
        
        conn.close()
        return result
    
    def get_active_logs(self):
        """Obtiene registros de deshidratación activos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM dehydration_logs
            WHERE status = 'In Progress'
        ''')
        
        rows = cursor.fetchall()
        
        # Obtener nombres de columnas
        column_names = [description[0] for description in cursor.description]
        
        # Convertir a lista de diccionarios
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))
        
        conn.close()
        return result
    
    def get_log_notifications(self, log_id):
        """Obtiene todas las notificaciones asociadas a un registro de deshidratación"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM notificaciones
            WHERE log_id = ?
            ORDER BY date
        ''', (log_id,))
        
        rows = cursor.fetchall()
        
        # Obtener nombres de columnas
        column_names = [description[0] for description in cursor.description]
        
        # Convertir a lista de diccionarios
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))
        
        conn.close()
        return result
    
    def get_dehydration_log(self, log_id):
        """Obtiene un registro específico de deshidratación"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM dehydration_logs
            WHERE id = ?
        ''', (log_id,))
        
        row = cursor.fetchone()
        
        if row:
            # Obtener nombres de columnas
            column_names = [description[0] for description in cursor.description]
            
            # Convertir a diccionario
            result = dict(zip(column_names, row))
            
            conn.close()
            return result
        else:
            conn.close()
            return None