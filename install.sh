#!/bin/bash
# Script d'installation complète de RavenTrace
# Combine l'environnement virtuel et les outils Kali en un seul script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Installation complète de RavenTrace             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si on est sur Kali
if ! grep -q "Kali" /etc/os-release 2>/dev/null; then
    echo -e "${YELLOW}⚠ Attention: Ce script est optimisé pour Kali Linux${NC}"
fi

# Mise à jour des repos
echo -e "${GREEN}[+] Mise à jour des repositories...${NC}"
sudo apt update -qq

# Installation des outils système
echo -e "${GREEN}[+] Installation des outils système...${NC}"
TOOLS="python3-pip python3-venv git curl whois dnsutils nmap dmitry whatweb pipx"

for tool in $TOOLS; do
    if ! dpkg -l | grep -q "^ii  $tool "; then
        echo -e "${YELLOW}  → Installation de $tool${NC}"
        sudo apt install -y $tool -qq
    else
        echo -e "${GREEN}  ✓ $tool déjà installé${NC}"
    fi
done

# Installation de theHarvester
echo -e "${GREEN}[+] Vérification de theHarvester...${NC}"
if ! command -v theHarvester &> /dev/null; then
    echo -e "${YELLOW}  → Installation de theHarvester${NC}"
    sudo apt install -y theharvester -qq
else
    echo -e "${GREEN}  ✓ theHarvester déjà installé${NC}"
fi

# Installation de Sherlock via pipx
echo -e "${GREEN}[+] Vérification de Sherlock...${NC}"
if ! command -v sherlock &> /dev/null; then
    echo -e "${YELLOW}  → Installation de Sherlock via pipx${NC}"
    pipx install sherlock-project
else
    echo -e "${GREEN}  ✓ Sherlock déjà installé${NC}"
fi

# Installation de holehe via pipx
echo -e "${GREEN}[+] Vérification de holehe...${NC}"
if ! command -v holehe &> /dev/null; then
    echo -e "${YELLOW}  → Installation de holehe via pipx${NC}"
    pipx install holehe
else
    echo -e "${GREEN}  ✓ holehe déjà installé${NC}"
fi

# Installation de maigret via pipx
echo -e "${GREEN}[+] Vérification de maigret...${NC}"
if ! command -v maigret &> /dev/null; then
    echo -e "${YELLOW}  → Installation de maigret via pipx${NC}"
    pipx install maigret
else
    echo -e "${GREEN}  ✓ maigret déjà installé${NC}"
fi

# Installation de phoneinfoga
echo -e "${GREEN}[+] Vérification de PhoneInfoga...${NC}"
if ! command -v phoneinfoga &> /dev/null; then
    echo -e "${YELLOW}  → Installation de PhoneInfoga${NC}"
    # Télécharger la dernière version
    PHONEINFOGA_VERSION=$(curl -s https://api.github.com/repos/sundowndev/phoneinfoga/releases/latest | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
    wget -q https://github.com/sundowndev/phoneinfoga/releases/download/v${PHONEINFOGA_VERSION}/phoneinfoga_Linux_x86_64.tar.gz
    tar -xzf phoneinfoga_Linux_x86_64.tar.gz
    sudo mv phoneinfoga /usr/local/bin/
    rm -f phoneinfoga_Linux_x86_64.tar.gz LICENSE README.md
    echo -e "${GREEN}  ✓ PhoneInfoga installé${NC}"
else
    echo -e "${GREEN}  ✓ PhoneInfoga déjà installé${NC}"
fi

# Créer l'environnement virtuel si il n'existe pas
if [ ! -d "venv" ]; then
    echo -e "${GREEN}[+] Création de l'environnement virtuel...${NC}"
    python3 -m venv venv
else
    echo -e "${YELLOW}[!] Environnement virtuel déjà existant${NC}"
fi

# Activer l'environnement virtuel
echo -e "${GREEN}[+] Activation de l'environnement virtuel...${NC}"
source venv/bin/activate

# Mettre à jour pip
echo -e "${GREEN}[+] Mise à jour de pip...${NC}"
pip install --upgrade pip

# Installer les dépendances Python
echo -e "${GREEN}[+] Installation des dépendances Python...${NC}"
pip install -r requirements.txt

# Installer les dépendances OSINT optionnelles
echo -e "${GREEN}[+] Installation des modules OSINT optionnels...${NC}"

# Essayer d'installer les modules OSINT un par un
OSINT_MODULES=(
    "holehe"
    "socialscan"
    "pwnedpasswords"
)

for module in "${OSINT_MODULES[@]}"; do
    echo -e "${YELLOW}  → Tentative d'installation de $module...${NC}"
    pip install $module 2>/dev/null && echo -e "${GREEN}    ✓ $module installé${NC}" || echo -e "${RED}    ✗ $module non disponible${NC}"
done

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            Installation terminée avec succès!             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Afficher les outils disponibles
echo -e "${GREEN}Outils OSINT disponibles:${NC}"
command -v theHarvester &> /dev/null && echo -e "  ${GREEN}✓${NC} theHarvester"
command -v sherlock &> /dev/null && echo -e "  ${GREEN}✓${NC} Sherlock"
command -v holehe &> /dev/null && echo -e "  ${GREEN}✓${NC} holehe"
command -v maigret &> /dev/null && echo -e "  ${GREEN}✓${NC} maigret"
command -v phoneinfoga &> /dev/null && echo -e "  ${GREEN}✓${NC} PhoneInfoga"
command -v dmitry &> /dev/null && echo -e "  ${GREEN}✓${NC} dmitry"
command -v whatweb &> /dev/null && echo -e "  ${GREEN}✓${NC} WhatWeb"
command -v nmap &> /dev/null && echo -e "  ${GREEN}✓${NC} Nmap"

echo ""
echo -e "${GREEN}Pour lancer RavenTrace:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate${NC}  (si pas déjà activé)"
echo -e "  ${YELLOW}python3 main.py interactive${NC}"
echo ""