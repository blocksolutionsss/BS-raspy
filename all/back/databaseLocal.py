import time, datetime, sqlite3

def setup_database():
    conn = sqlite3.connect('deshidratador.db')
    cursor = conn.cursor()

    # Crear tabla para almacenar datos hist�ricos de los dispositivos
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



def save_historical_data(device, temperature, humidity, gas, weight, status='activated', duration=0.0):
    conn = sqlite3.connect('deshidratador.db')
    cursor = conn.cursor()
    
    # Registrar la hora de inicio
    start_time = time.time()
    
    cursor.execute('''
        INSERT INTO data_history (device, temperature, humidity, gas, weight, status, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (device, temperature, humidity, gas, weight, status, duration))
    
    conn.commit()
    conn.close()
    
    # Calcular la duraci�n y actualizar el estado si es necesario
    end_time = time.time()
    duration = end_time - start_time  # Duraci�n en segundos

    # Actualizar estado a 'completed' y duraci�n
    conn = sqlite3.connect('deshidratador.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE data_history
        SET status = ?, duration = ?
        WHERE device = ? AND status = 'activated'
    ''', ('completed', duration, device))
    conn.commit()
    conn.close()

    print("Datos historicos guardados en la base de datos con estado y duracion.")

def save_notification(notification_type, value, description, priority, log_id):
    conn = sqlite3.connect('deshidratador.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notificaciones (type, value, description, priority, date, log_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (notification_type, value, description, priority, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), log_id))
    conn.commit()
    conn.close()
    print(f"Notificacion '{description}' guardada para el historial con ID {log_id}.")

