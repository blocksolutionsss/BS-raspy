
import time

from back import socket_connection
from back import databaseLocal
from back import rabbit
from back import esp32
from front.app import app



def main():
    # Configurar la base de datos
    databaseLocal.setup_database()
    print("Base de datos configurada.")

    # Iniciar el hilo de conexion de Socket.IO
    socket_connection.start_socketio_thread()

    # Iniciar el hilo de RabbitMQ
    rabbit.start_rabbitmq_thread()

    #inicar el hilo de esp32
    
    esp32.start_serial_esp32()

    app.mainloop()
    # Mantener el programa principal en ejecuci�n
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
