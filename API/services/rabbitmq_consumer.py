import json
import pika
from flask import jsonify

from API.clients import clients_blueprint
from API.services.pika_config import get_rabbitmq_connection


# A global variable to store notifications
order_notifications = []




# Route to get all notifications
@clients_blueprint.route('/notifications', methods=['GET'])
def get_notifications():
    return jsonify(order_notifications), 200


# RabbitMQ consumer for order notifications
def consume_order_notifications():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.exchange_declare(exchange='order_notifications', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='order_notifications', queue=queue_name)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        formatted_message = f"Received order notification for client: {message}"

        # Store the formatted notification
        order_notifications.append(formatted_message)
        # Logic to send notification to client
        print(f"Received order notification for client: {message}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()



