#!/bin/sh

echo "Exécution de l'initialisation de la base de données (création des tables et insertion des données de test)..."

# Exécute directement le script init_db.py, qui contient l'appel à db.create_all() et l'insertion des données.
# Nous devons utiliser "python /app/init_db.py" car init_db.py a la clause 'if __name__ == "__main__":'
/usr/bin/env python /app/init_db.py

echo "Démarrage du serveur Flask..."
exec flask run --host=0.0.0.0