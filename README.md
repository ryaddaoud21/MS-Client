
# MS-Client

## Microservice Client

### Description

Le microservice `Client` gère les informations des clients. Il permet de créer, lire, mettre à jour et supprimer des clients dans une base de données MySQL. De plus, il expose des métriques pour la surveillance via Prometheus et Grafana.

### Architecture
![Ajouter un sous-titre (2)](https://github.com/user-attachments/assets/743a9b51-b5b6-4fb2-91f1-b8c0b08cc635)

Le microservice `MS-Client` fait partie d'une architecture microservices plus large, qui comprend également :

- **MS-Produit** : Microservice pour la gestion des produits.
- **MS-Commande** : Microservice pour la gestion des commandes.
- **RabbitMQ** : Service de messagerie pour la communication entre les microservices.
- **Prometheus** : Outil de surveillance pour collecter les métriques des microservices.
- **Grafana** : Plateforme d'analyse et de visualisation des métriques Prometheus.
- **MySQL** : Base de données pour les microservices `Client`, `Produit` et `Commande`.

### Architecture Diagram

In this architecture, each microservice communicates with others via **RabbitMQ**. All services are containerized using **Docker**, and the application is orchestrated using **Docker Compose**. **Prometheus** is used for scraping metrics from the microservices, and **Grafana** visualizes those metrics.

**Ports Setup:**

- **Client Service**: Port `5001` is mapped for external access to the client microservice.
- **Produit Service**: Port `5002` is exposed for the product microservice.
- **Commande Service**: Port `5003` is used for the order microservice.
- **Prometheus**: Runs on port `9090` and scrapes metrics from all microservices.
- **Grafana**: Runs on port `3000`, where dashboards for visualizing the metrics can be accessed.
- **RabbitMQ**: The default ports `5672` and `15672` are used for message handling and the management interface, respectively.

### Prérequis

Avant de commencer, assurez-vous que vous avez installé les éléments suivants :

- **Docker** : Utilisé pour exécuter les conteneurs.
- **Docker Compose** : Utilisé pour orchestrer plusieurs conteneurs Docker.
- **Prometheus** : Utilisé pour surveiller les performances des microservices.
- **Grafana** : Utilisé pour visualiser les métriques collectées par Prometheus.
- **Git** : Pour cloner les dépôts de microservices.
  
### Installation et Démarrage avec Docker Compose

1. **Clonez le dépôt du microservice Client**:

   ```bash
   git clone https://github.com/ryaddaoud21/MS-Client.git
   cd MS-Client
   ```

2. **Clonez le dépôt du fichier `docker-compose.yml`**:

   ```bash
   git clone https://github.com/ryaddaoud21/microservices-deployment
   cd microservices-deployment
   ```

   This file orchestrates all the services necessary, including Prometheus, Grafana, RabbitMQ, MySQL, and the microservices.

3. **Démarrez tous les services**:

   ```bash
   docker-compose up -d
   ```

   This command will launch the microservices, RabbitMQ, Prometheus, and Grafana, all in detached mode.

4. **Vérifiez que les services sont démarrés correctement**:

   ```bash
   docker-compose ps
   ```

5. **Accédez aux interfaces**:

   - **Client API**: `http://localhost:5001`
   - **Produit API**: `http://localhost:5002`
   - **Commande API**: `http://localhost:5003`
   - **Prometheus**: `http://localhost:9090`
   - **Grafana**: `http://localhost:3000`
   - **RabbitMQ**: `http://localhost:15672` (default login: `guest`, password: `guest`)

6. **Lancer les tests unitaires**:

   To run the unit tests for the `MS-Client` service, use the following command:

   ```bash
   python -m unittest discover -s TEST
   ```

   For running the tests on all microservices, navigate to each microservice directory and repeat this command.

### Endpoints

Here are the main endpoints exposed by the `Client` microservice:

- **POST** `/login` : Authenticate and generate a token.
- **GET** `/customers` : Fetch the list of all clients.
- **GET** `/customers/<id>` : Retrieve details of a specific client.
- **POST** `/customers` : Create a new client (admin only).
- **PUT** `/customers/<id>` : Update the information of a specific client (admin only).
- **DELETE** `/customers/<id>` : Delete a specific client (admin only).

### Monitoring and Visualization

- **Prometheus**: Collects the metrics from the microservices. Each microservice has an exposed `/metrics` endpoint, which Prometheus scrapes regularly.
  
  Example: 
  ```yaml
  scrape_configs:
    - job_name: 'ms-client'
      static_configs:
        - targets: ['client-service:5001']
  ```

- **Grafana**: Use Grafana to visualize the metrics collected by Prometheus. Dashboards can be created to monitor the performance, request latency, and resource utilization of the microservices.

### Folder Structure

Here’s the project folder structure for `MS-Client`:

```
MS-Client/
├── .github/                # GitHub configuration files for CI/CD pipelines
├── .idea/                  # IDE-specific configuration files (PyCharm, etc.)
├── API/                    # Main API directory
│   ├── services/           # Supporting services like RabbitMQ configurations
│   ├── auth.py             # Authentication logic for token validation
│   ├── clients.py          # Main endpoints for client CRUD operations
│   ├── config.py           # Flask configuration settings
│   ├── models.py           # Database models for the clients
├── TEST/                   # Unit tests for the API
│   ├── test_clients.py     # Unit tests for client-related API operations
├── Dockerfile              # Dockerfile to containerize the microservice
├── README.md               # Project documentation
├── client_api.py           # Main entry point for the client microservice
├── requirements.txt        # Python dependencies for the project
```

This structure ensures that the microservice follows good practices, with clear separation between API endpoints, services, and testing logic.
