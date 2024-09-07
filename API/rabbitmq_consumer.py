import json
import threading
from .pika_config import get_rabbitmq_connection

# Consommateur RabbitMQ pour les notifications de commande
def consume_order_notifications():
    connection = get_rabbitmq_connection()  # Récupérer la connexion RabbitMQ depuis le fichier pika_config
    channel = connection.channel()

    # Déclarer un échange de type "fanout" pour les notifications de commande
    channel.exchange_declare(exchange='order_notifications', exchange_type='fanout')

    # Créer une file d'attente anonyme exclusive pour recevoir les messages
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Lier la file d'attente à l'échange
    channel.queue_bind(exchange='order_notifications', queue=queue_name)

    # Callback pour traiter les messages reçus
    def callback(ch, method, properties, body):
        message = json.loads(body)
        # Logique pour envoyer la notification au client
        print(f"Notification de commande reçue pour le client : {message}")

    # Commence à consommer les messages de la file d'attente
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

# Fonction pour démarrer le consommateur RabbitMQ dans un thread séparé
def start_consumer_in_thread():
    threading.Thread(target=consume_order_notifications, daemon=True).start()
