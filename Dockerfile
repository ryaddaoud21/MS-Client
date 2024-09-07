FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Installer les dépendances, y compris waitress
RUN pip install --no-cache-dir -r requirements.txt waitress


EXPOSE 5001

CMD ["waitress-serve", "--port=5001", "client_api:app"]
