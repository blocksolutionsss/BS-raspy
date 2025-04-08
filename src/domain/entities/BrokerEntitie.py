from pika import channel as Channel
from pika import ConnectionParameters, PlainCredentials, BlockingConnection, BasicProperties
import json
from typing import Dict, Any, Callable, Optional

class BrokerEntitie:
    """
    Class representing a broker entity.
    """
    protocol: str = "amqp"
    ip: str = "54.164.116.230"
    port: int = 5672
    user: str = "blocksolutions-rasp"
    password: str = "leedpees"
    
    channel: Channel
    exchange: str = ""
    connection = None

    def __init__(self):
        self.create_chanel()
        
    def create_chanel(self):
        """
        Create a channel for the broker.
        """
        # Create credentials object
        credentials = PlainCredentials(
            username=self.user,
            password=self.password
        )
        
        # Setup connection parameters
        parameters = ConnectionParameters(
            host=self.ip,
            port=self.port,
            credentials=credentials
        )
        
        # Establish connection
        self.connection = BlockingConnection(parameters)
        
        # Create and store the channel
        self.channel = self.connection.channel()
        
        # If exchange is specified, you might want to declare it
        if self.exchange:
            # You can add exchange_type and other parameters as needed
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='direct')
    
    def publish(self, routing_key: str, message: Dict[str, Any]) -> bool:
        """
        Publish a message to a specific queue.
        
        Args:
            routing_key (str): The routing key or queue name.
            message (Dict[str, Any]): The message to be published as a dictionary.
            exchange (str, optional): The exchange to use. Defaults to self.exchange.
            
        Returns:
            bool: True if message was published successfully, False otherwise.
        """
        try:
            
            # Convert the message to JSON
            message_body = json.dumps(message)
            
            # Define message properties
            properties = BasicProperties(
                content_type='application/json',
                delivery_mode=2,  # Persistent message
            )
            
            # Publish the message
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message_body,
                properties=properties
            )
            
            return True
        except Exception as e:
            print(f"Error publishing message: {e}")
            return False
    
    def consume(self, queue_name: str, callback: Callable, auto_ack: bool = True) -> None:
        """
        Start consuming messages from a specific queue.
        
        Args:
            queue_name (str): The name of the queue to consume from.
            callback (Callable): The callback function to handle received messages.
            auto_ack (bool, optional): Whether to automatically acknowledge messages. Defaults to True.
        """
        try:
            # Ensure the queue exists
            self.channel.queue_declare(queue=queue_name, durable=True, auto_delete=False)
            
            # Start consuming
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            
            print(f"Started consuming from queue: {queue_name}")
            self.channel.start_consuming()
        except Exception as e:
            print(f"Error consuming messages: {e}")
    
    def declare_queue(self, queue_name: str, durable: bool = True, 
                     exclusive: bool = False, auto_delete: bool = False,
                     arguments: Optional[Dict[str, Any]] = None) -> None:
        """
        Declare a queue.
        
        Args:
            queue_name (str): The name of the queue to declare.
            durable (bool, optional): Whether the queue should survive broker restarts. Defaults to True.
            exclusive (bool, optional): Whether the queue is exclusive. Defaults to False.
            auto_delete (bool, optional): Whether the queue should be deleted when no longer used. Defaults to False.
            arguments (Dict[str, Any], optional): Additional arguments for the queue. Defaults to None.
        """
        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            arguments=arguments
        )
    
    def bind_queue(self, queue_name: str, exchange: str, routing_key: str) -> None:
        """
        Bind a queue to an exchange with a routing key.
        
        Args:
            queue_name (str): The name of the queue to bind.
            exchange (str): The exchange to bind to.
            routing_key (str): The routing key to use for binding.
        """
        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange,
            routing_key=routing_key
        )
    
    def close(self) -> None:
        """
        Close the channel and connection.
        """
        if self.channel and self.channel.is_open:
            self.channel.close()
        
        if self.connection and self.connection.is_open:
            self.connection.close()
            
    def __del__(self) -> None:
        """
        Destructor to ensure connections are closed.
        """
        self.close()