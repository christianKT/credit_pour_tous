# Utiliser une image officielle Python
FROM python:3.10-slim

# Installer la dépendance système manquante
RUN apt-get update && apt-get install -y libgomp1

# Définir le répertoire de travail
WORKDIR /app

# Copier tous les fichiers du projet dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port de Flask
EXPOSE 5000

# Lancer l'application Flask
CMD ["python", "app.py"]
