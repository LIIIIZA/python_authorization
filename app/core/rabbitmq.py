import json
import pika
import logging
from typing import Optional, Dict, Any
from pika.adapters.blocking_connection import BlockingChannel
from app.core.config import settings

logger = logging.getLogger(__name__)

class RabbitMQManager:
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[BlockingChannel] = None
        self.exchange_name = settings.RABBITMQ_EXCHANGE
        self.queue_name = settings.RABBITMQ_QUEUE
        self.routing_key = settings.RABBITMQ_ROUTING_KEY

    def connect(self) -> None:
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(settings.RABBITMQ_URL))
            self.channel = self.connection.channel()
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"RabbitMQ connection error: {str(e)}")
            raise

    def close(self) -> None:
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

    def declare_exchange(self, exchange_type: str = 'direct') -> None:
        if not self.channel:
            raise RuntimeError("Channel not initialized")
        
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type=exchange_type,
            durable=True
        )
        logger.debug(f"Exchange declared: {self.exchange_name}")

    def declare_queue(self) -> None:
        if not self.channel:
            raise RuntimeError("Channel not initialized")
        
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            arguments={
                'x-message-ttl': 86400000  # 24 часа
            }
        )
        logger.debug(f"Queue declared: {self.queue_name}")

    def bind_queue(self) -> None:
        if not self.channel:
            raise RuntimeError("Channel not initialized")
        
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=self.queue_name,
            routing_key=self.routing_key
        )
        logger.debug(f"Queue {self.queue_name} bound to {self.exchange_name}")

    def publish_message(
        self, 
        message: Dict[str, Any], 
        expiration: Optional[int] = None
    ) -> bool:
        try:
            if not self.channel or not self.connection.is_open:
                self.connect()
                self.declare_exchange()
                self.declare_queue()
                self.bind_queue()

            properties = pika.BasicProperties(
                delivery_mode=2,  
                expiration=str(expiration) if expiration else None
            )

            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=json.dumps(message),
                properties=properties
            )
            logger.debug(f"Message published: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            return False

    def __enter__(self):
        self.connect()
        self.declare_exchange()
        self.declare_queue()
        self.bind_queue()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

rabbitmq_manager = RabbitMQManager()