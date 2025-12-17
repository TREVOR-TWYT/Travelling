#!/bin/bash

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "=========================================="
echo "   🚀 DÉPLOIEMENT MBOA TRAVEL 🚌"
echo "=========================================="
echo -e "${NC}"

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé!${NC}"
    echo "Installez Docker avec le script fourni"
    exit 1
fi

# Vérifier que le service Docker est actif
if ! sudo systemctl is-active --quiet docker; then
    echo -e "${YELLOW}⚠️  Le service Docker n'est pas actif${NC}"
    echo -e "${YELLOW}Démarrage du service Docker...${NC}"
    sudo systemctl start docker
    sleep 2
fi

echo -e "${GREEN}✅ Docker est prêt${NC}"

# Arrêter les conteneurs existants
echo -e "${YELLOW}📦 Arrêt des conteneurs existants...${NC}"
docker compose down 2>/dev/null || true

# Construire les images
echo -e "${YELLOW}🔨 Construction des images Docker...${NC}"
docker compose build

# Démarrer les conteneurs
echo -e "${YELLOW}🚀 Démarrage des conteneurs...${NC}"
docker compose up -d

# Attendre que la base de données soit prête
echo -e "${YELLOW}⏳ Attente de la base de données...${NC}"
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U trevor > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Base de données prête!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Initialiser la base de données
echo -e "${YELLOW}🗄️  Initialisation de la base de données...${NC}"
docker compose exec web python init_db.py

# Afficher le statut
echo -e "${GREEN}"
echo "=========================================="
echo "   ✅ DÉPLOIEMENT TERMINÉ!"
echo "=========================================="
echo -e "${NC}"

docker compose ps

echo ""
echo -e "${GREEN}🎉 Application disponible:${NC}"
echo -e "   🌐 Site public: ${BLUE}http://localhost:5000${NC}"
echo -e "   🔐 Admin: ${BLUE}http://localhost:5000/admin-login${NC}"
echo -e "   📊 Stats: ${BLUE}http://localhost:5000/admin/statistiques${NC}"
echo ""
echo -e "${YELLOW}📋 Identifiants admin par défaut:${NC}"
echo -e "   Username: ${GREEN}admin${NC}"
echo -e "   Password: ${GREEN}admin${NC}"
echo ""
echo -e "${YELLOW}📝 Commandes utiles:${NC}"
echo -e "   Logs: ${BLUE}docker compose logs -f${NC}"
echo -e "   Arrêter: ${BLUE}docker compose stop${NC}"
echo -e "   Redémarrer: ${BLUE}docker compose restart${NC}"
echo -e "   Supprimer: ${BLUE}docker compose down -v${NC}"
echo ""