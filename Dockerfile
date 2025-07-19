# Utiliser une image officielle Python
FROM python:3.10-slim

# Installer la dépendance système manquante
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier tous les fichiers du projet dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Définir la variable d'environnement Flask
ENV FLASK_ENV=production

# Commande de démarrage
CMD gunicorn app:app --bind 0.0.0.0:$PORT