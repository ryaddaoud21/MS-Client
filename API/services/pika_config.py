import json
import pika
import time

def get_rabbitmq_connection():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq', port=5672))
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ n'est pas encore disponible. Nouvelle tentative dans 5 secondes...")
            time.sleep(5)

def get_channel():
    connection = get_rabbitmq_connection()
    return connection.channel()

def publish_message(exchange, message):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='fanout')

    channel.basic_publish(
        exchange=exchange,
        routing_key='',
        body=json.dumps(message)
    )
    connection.close()
