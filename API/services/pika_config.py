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


def publish_message(queue_name, message):
    try:
        # Obtenir la connexion à RabbitMQ
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        # Déclarer la file d'attente
        channel.queue_declare(queue=queue_name, durable=True)

        # Publier le message dans RabbitMQ
        channel.basic_publish(
            exchange='',  # Pas d'exchange, utilisation du routing_key direct
            routing_key=queue_name,
            body=json.dumps(message),  # Convertir le message en JSON
            properties=pika.BasicProperties(
                delivery_mode=2,  # Rendre le message persistant
            )
        )

        # Fermer le canal et la connexion après la publication
        channel.close()
        connection.close()

    except Exception as e:
        # Gérer les exceptions liées à RabbitMQ
        print(f"Erreur lors de l'envoi du message à RabbitMQ: {str(e)}")
        raise