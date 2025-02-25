import json
import logging
import pika
from app.core.config import settings
from .telegram import telegram

logger = logging.getLogger(__name__)

class NotificationWorker:
    def __init__(self):
        self.connection_params = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
        )
        
    def callback(self, ch, method, properties, body):
        """Обработчик сообщений из очереди"""
        try:
            message = json.loads(body)
            email = message.get('email')
            
            if not email:
                raise ValueError("Invalid message format")
            
            text = telegram.format_welcome_message(email)
            if telegram.send_message(text):
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        """Запускает потребителя очереди"""
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        channel.queue_declare(
            queue='registrations',
            durable=True,
            arguments={
                'x-message-ttl': 86400000  # 24 часа
            }
        )
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='registrations',
            on_message_callback=self.callback
        )
        
        logger.info("Worker started. Waiting for messages...")
        channel.start_consuming()

if __name__ == "__main__":
    worker = NotificationWorker()
    worker.run()
