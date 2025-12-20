# Utiliser Python 3.10 comme image de base
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-dotenv

# Copier tout le code de l'application
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p templates/errors static/css static/image

# Exposer le port 5000
EXPOSE 5000

# Variables d'environnement
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Commande de démarrage
CMD ["flask", "run", "--host=0.0.0.0"]