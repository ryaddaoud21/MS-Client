import json
import pika
from API.services.pika_config import get_rabbitmq_connection

# RabbitMQ consumer for order notifications
def consume_order_notifications():
    # Establish a connection to RabbitMQ
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    # Declare the exchange
    channel.exchange_declare(exchange='order_notifications', exchange_type='fanout')

    # Create a queue that will receive messages from the exchange
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind the queue to the exchange to start receiving messages
    channel.queue_bind(exchange='order_notifications', queue=queue_name)

    # Define the callback function to process received messages
    def callback(ch, method, properties, body):
        message = json.loads(body)
        # Logic to process the order notification for the client
        print(f"Received order notification for client: {message}")

    # Start consuming messages
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    # Begin the RabbitMQ consumer loop
    channel.start_consuming()
