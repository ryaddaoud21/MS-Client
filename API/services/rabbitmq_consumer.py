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
        formatted_message = f"Received order notification: {message}"

        # Store the formatted notification
        order_notifications.append(formatted_message)
        # Logic to send notification to client
        print(f"Received order notification for client: {message}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def verify_token(token):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='auth_requests')

    message = {'token': token}
    channel.basic_publish(exchange='', routing_key='auth_requests', body=json.dumps(message))

    # Listen for the response
    response = None
    for method_frame, properties, body in channel.consume('auth_responses', inactivity_timeout=1):
        if body:
            response = json.loads(body)
        break

    connection.close()
    formatted_message = f"User authenticated"

    # Store the formatted notification
    order_notifications.append(formatted_message)
    return response.get('authenticated', False), response.get('role')