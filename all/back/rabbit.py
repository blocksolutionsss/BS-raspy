import json
import pika
import threading
import time

# Configuraci�n para RabbitMQ
rabbit_settings = {
    'protocol': 'amqp',
    'hostname': '54.164.116.230',
    'port': 5672,
    'username': 'blocksolutions-rasp',
    'password': 'leedpees'
}

channel = None
exchange = None

# Establece las credenciales y par�metros de conexi�n
def create_rabbit_connection():
    global channel, exchange
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
    return connection



def send_notification(routing_key, notification):
    """Envia el mensaje a RabbitMQ."""
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(notification)
    )
    print(f"Notificación enviada: {notification}")

def start_rabbitmq_thread():
    """Inicia el hilo que maneja la conexion y envio a RabbitMQ."""
    rabbitmq_thread = threading.Thread(target=create_rabbit_connection)
    rabbitmq_thread.daemon = True  # El hilo se cierra cuando el programa principal termina
    rabbitmq_thread.start()
    print("Servidor RabbitMQ iniciado en un hilo.")

