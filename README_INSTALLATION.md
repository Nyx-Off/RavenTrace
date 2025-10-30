# Guide d'Installation RavenTrace sur Kali Linux

## Installation Rapide
```bash
# 1. Cloner ou extraire le projet
cd RavenTrace/

# 2. Donner les permissions aux scripts
chmod +x *.sh

# 3. Installation automatique complète
./setup_venv.sh

# 4. Lancer RavenTrace
source venv/bin/activate
python3 main.py interactive
```

## Installation Manuelle Détaillée

### Étape 1 : Environnement Virtuel Python
```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip
```

### Étape 2 : Installer les dépendances Python
```bash
# Dans le venv activé
pip install -r requirements.txt
```

### Étape 3 : Installer les outils Kali
```bash
# Installer les outils système
sudo apt update
sudo apt install -y python3-pip python3-venv git curl whois dnsutils nmap dmitry whatweb pipx

# Installer les outils OSINT via pipx
pipx install sherlock-project
pipx install holehe
pipx install maigret

# Installer theHarvester
sudo apt install -y theharvester

# Installer PhoneInfoga
wget https://github.com/sundowndev/phoneinfoga/releases/latest/download/phoneinfoga_Linux_x86_64.tar.gz
tar -xzf phoneinfoga_Linux_x86_64.tar.gz
sudo mv phoneinfoga /usr/local/bin/
rm phoneinfoga_Linux_x86_64.tar.gz
```

## Résolution des Problèmes

### Erreur "externally-managed-environment"

Sur les versions récentes de Kali, utilisez toujours un environnement virtuel :
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Modules manquants

Certains modules OSINT sont optionnels. Si non disponibles, le programme fonctionnera sans eux :
- holehe
- socialscan
- maigret
- h8mail

### Permissions

Si erreur de permissions :
```bash
chmod +x *.sh
sudo chown -R $USER:$USER ~/.raven_trace
```

## Configuration des API Keys (Optionnel)

Éditez `config.yaml` et ajoutez vos clés API :
```yaml
apis:
  hibp_api_key: "votre-clé-ici"
  hunter_api_key: "votre-clé-ici"
  shodan_api_key: "votre-clé-ici"
  # etc...
```

## Utilisation

### Mode Interactif
```bash
python3 main.py interactive
```

### Recherche Directe
```bash
# Email
python3 main.py email target@example.com --deep

# Username
python3 main.py username johndoe --export json

# Téléphone
python3 main.py phone +33612345678 --country FR
```

## Vérifier l'Installation
```bash
# Vérifier les outils installés
which theHarvester
which sherlock
which holehe
which phoneinfoga

# Vérifier les modules Python
python3 -c "import requests; import phonenumbers; import dns.resolver; print('✓ Modules OK')"
```