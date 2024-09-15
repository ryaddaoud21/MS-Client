from flask import Flask
from API.models import db
from API.clients import clients_blueprint
from API.auth import auth_blueprint
from threading import Thread
from API.services.rabbitmq_consumer import consume_order_notifications
from API.config import Config
from prometheus_client import multiprocess, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

app.config.from_object(Config)
#app.config['DEBUG'] = True

# Initialize the database
db.init_app(app)
app.register_blueprint(auth_blueprint, url_prefix='/')
app.register_blueprint(clients_blueprint, url_prefix='/')

# Register the blueprints
#app.register_blueprint(clients_blueprint)
#app.register_blueprint(auth_blueprint)


@app.route('/metrics')
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return generate_latest(registry), 200, {'Content-Type': CONTENT_TYPE_LATEST}



if __name__ == '__main__':
    Thread(target=consume_order_notifications, daemon=True).start()
    app.run(host='0.0.0.0', port=5001)