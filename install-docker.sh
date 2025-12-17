#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🐳 Installation de Docker${NC}"

# Vérifier si déjà installé
if command -v docker &> /dev/null && sudo systemctl is-active --quiet docker; then
    echo -e "${GREEN}✅ Docker est déjà installé et actif${NC}"
    docker --version
    docker compose version
    exit 0
fi

echo -e "${YELLOW}📦 Installation en cours...${NC}"

# Désinstaller les anciennes versions
echo "Nettoyage des anciennes installations..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc docker-compose 2>/dev/null || true

# Mettre à jour le système
echo "Mise à jour du système..."
sudo apt-get update

# Installer les dépendances
echo "Installation des dépendances..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Ajouter la clé GPG de Docker
echo "Ajout de la clé GPG Docker..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Ajouter le dépôt Docker
echo "Ajout du dépôt Docker..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
echo "Installation de Docker..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Démarrer Docker
echo "Démarrage du service Docker..."
sudo systemctl start docker
sudo systemctl enable docker

# Ajouter l'utilisateur au groupe docker
echo "Configuration des permissions..."
sudo usermod -aG docker $USER

# Vérifier l'installation
echo ""
echo -e "${GREEN}✅ Installation terminée!${NC}"
echo ""
echo "Versions installées:"
docker --version
docker compose version

echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "Vous devez vous déconnecter et reconnecter pour que les permissions prennent effet"
echo "Ou exécutez: newgrp docker"
echo ""
echo -e "${GREEN}Test de Docker:${NC}"
docker run hello-world

echo ""
echo -e "${GREEN}🎉 Docker est prêt à être utilisé!${NC}"