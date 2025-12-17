# 🐳 Guide Docker - MBOA TRAVEL

## 📋 Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 5GB espace disque

## 🚀 Installation Rapide

### 1. Installation de Docker

#### Ubuntu/Debian
```bash
# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajouter utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker

# Vérifier
docker --version
docker compose version
```

#### Mac
```bash
# Télécharger Docker Desktop
# https://www.docker.com/products/docker-desktop

# Ou via Homebrew
brew install --cask docker
```

#### Windows
```bash
# Télécharger Docker Desktop
# https://www.docker.com/products/docker-desktop

# Installer WSL2 si nécessaire
wsl --install
```

## 🎯 Démarrage

### Méthode 1: Script automatique (recommandé)
```bash
./deploy.sh
```

### Méthode 2: Commandes manuelles
```bash
# 1. Construire et démarrer
docker compose up --build -d

# 2. Attendre 15 secondes

# 3. Initialiser la DB
docker compose exec web python init_db.py

# 4. Accéder à l'application
# http://localhost:5000
```

## 📊 Accès à l'application

| Service | URL | Identifiants |
|---------|-----|--------------|
| Site Public | http://localhost:5000 | - |
| Admin | http://localhost:5000/admin-login | admin / admin |
| Stats | http://localhost:5000/admin/statistiques | - |
| Liens Rapides | http://localhost:5000/liens-rapides | - |

## 🛠️ Commandes Docker

### Gestion des conteneurs
```bash
# Démarrer
docker compose up -d

# Arrêter
docker compose stop

# Redémarrer
docker compose restart

# Supprimer (conserve les données)
docker compose down

# Supprimer tout (données incluses)
docker compose down -v

# Reconstruire après modification
docker compose up --build -d
```

### Logs et monitoring
```bash
# Tous les logs
docker compose logs -f

# Logs de l'app uniquement
docker compose logs -f web

# Logs de la DB
docker compose logs -f db

# Dernières 100 lignes
docker compose logs --tail=100 web

# État des conteneurs
docker compose ps

# Ressources utilisées
docker stats
```

### Accès aux conteneurs
```bash
# Shell dans le conteneur web
docker compose exec web bash

# Shell dans PostgreSQL
docker compose exec db psql -U trevor -d travelling

# Exécuter une commande Python
docker compose exec web python -c "from app import db; print(db)"

# Réinitialiser la DB
docker compose exec web python init_db.py
```

## 🗄️ Base de données

### Connexion directe à PostgreSQL
```bash
docker compose exec db psql -U trevor -d travelling
```

Commandes SQL utiles:
```sql
-- Lister les tables
\dt

-- Voir les clients
SELECT * FROM client LIMIT 5;

-- Compter les réservations
SELECT COUNT(*) FROM reservation;

-- Quitter
\q
```

### Sauvegarde
```bash
# Sauvegarder
docker compose exec db pg_dump -U trevor travelling > backup_$(date +%Y%m%d).sql

# Restaurer
docker compose exec -T db psql -U trevor travelling < backup_20250107.sql
```

### Migrations Flask-Migrate
```bash
# Créer une nouvelle migration
docker compose exec web flask db migrate -m "Description"

# Appliquer les migrations
docker compose exec web flask db upgrade

# Revenir en arrière
docker compose exec web flask db downgrade
```

## 🐛 Dépannage

### Erreur: Port déjà utilisé
```bash
# Trouver le processus utilisant le port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Changer le port dans docker-compose.yml
ports:
  - "8000:5000"  # Utiliser le port 8000 au lieu de 5000
```

### Erreur de connexion à la DB
```bash
# Vérifier que la DB est prête
docker compose exec db pg_isready -U trevor

# Voir les logs de la DB
docker compose logs db

# Redémarrer la DB
docker compose restart db
```

### Conteneur qui redémarre en boucle
```bash
# Voir les logs
docker compose logs web

# Vérifier la syntaxe Python
docker compose exec web python -m py_compile app.py
```

### Nettoyer complètement
```bash
# Tout arrêter et supprimer
docker compose down -v

# Supprimer les images
docker rmi mboa_travel_app postgres:15-alpine

# Nettoyer le système
docker system prune -a --volumes

# Recommencer
docker compose up --build -d
```

### Erreur de permissions
```bash
# Donner les permissions
chmod -R 755 static templates

# Rebuilder
docker compose up --build -d
```

## 📈 Performance

### Limiter les ressources

Ajoutez dans `docker-compose.yml`:
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Optimiser les images
```bash
# Voir la taille des images
docker images

# Nettoyer les images inutilisées
docker image prune -a
```

## 🔐 Sécurité (Production)

### Changez les mots de passe

1. Modifiez `.env`:
```env
POSTGRES_PASSWORD=VotreMotDePasseSecurise
SECRET_KEY=VotreCleSecrete
```

2. Recréez les conteneurs:
```bash
docker compose down -v
docker compose up -d
```

### Ne pas exposer PostgreSQL

Dans `docker-compose.yml`, retirez:
```yaml
ports:
  - "5432:5432"  # Commentez cette ligne
```

## 🌐 Déploiement Production

### Avec Nginx

Créez `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/app/static:ro
    depends_on:
      - web
    networks:
      - mboa_network
```

Démarrez avec:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📞 Support

- Documentation Flask: https://flask.palletsprojects.com/
- Documentation Docker: https://docs.docker.com/
- PostgreSQL: https://www.postgresql.org/docs/

## 📝 Changelog

- **v1.0** (2025-01-07): Première version dockerisée