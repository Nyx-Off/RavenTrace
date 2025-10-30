#!/bin/bash
# Script d'installation complète avec environnement virtuel

echo "╔══════════════════════════════════════════════════════════╗"
echo "║      Setup complet de RavenTrace avec venv               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# Installer les outils système
echo -e "${GREEN}[+] Installation des outils système Kali...${NC}"
bash install_kali_tools.sh

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                Setup terminé avec succès!                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Pour lancer RavenTrace:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate${NC}  (si pas déjà activé)"
echo -e "  ${YELLOW}python3 main.py interactive${NC}"
echo ""