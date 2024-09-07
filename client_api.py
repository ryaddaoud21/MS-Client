from flask import Flask
from API.models import db
from API.clients import clients_blueprint
from API.auth import auth_blueprint
from threading import Thread
from API.services.rabbitmq_consumer import consume_order_notifications
from API.config import Config

app = Flask(__name__)

app.config.from_object(Config)


# Initialize the database
db.init_app(app)

# Register the blueprints
app.register_blueprint(clients_blueprint)
app.register_blueprint(auth_blueprint)

if __name__ == '__main__':
    Thread(target=consume_order_notifications, daemon=True).start()
    app.run(host='0.0.0.0', port=5001)
