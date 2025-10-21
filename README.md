# 🐦 RavenTrace v1.0.0

**Advanced OSINT Intelligence Tool** - Recherche intelligente par Email, Téléphone et Pseudo

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## 📋 Table des Matières

- [Caractéristiques](#caractéristiques)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [API](#api)
- [Architecture](#architecture)
- [Avertissements Légaux](#avertissements-légaux)

## ✨ Caractéristiques

### 📧 Email Lookup
- **Vérification Réputation** via EmailRep.io
- **Analyse DNS** (MX, SPF, DMARC)
- **Détection Fuites** (Have I Been Pwned)
- **Recherche Profils Sociaux**
- **Vérification Domaine** (WHOIS)

### 📱 Phone Lookup
- **Identification Opérateur** (Carrier)
- **Géolocalisation** (Région, Pays)
- **Vérification Réputation** (TrueCaller, NumVerify)
- **Détection VoIP**
- **Recherche Agrégateurs de Données**

### 👤 Username Lookup
- **Recherche Multi-Platformes** (20+ réseaux)
- **GitHub API** (Profils, Repos, Followers)
- **Reddit** (Karma, Posts, Subs)
- **Forums** (StackOverflow, Medium, Dev.to)
- **Recherche Parallélisée** (Performance optimale)

### 🔧 Fonctionnalités Avancées
- ✅ **Cache SQLite** (24h TTL par défaut)
- ✅ **Exports Multi-formats** (JSON, CSV, HTML)
- ✅ **Rapports Détaillés** avec recommandations
- ✅ **CLI Complète** (CLI + Mode Interactif)
- ✅ **Logging Avancé** (Fichier + Console)
- ✅ **Rate Limiting** (Respectueux des serveurs)
- ✅ **User-Agent Rotation** (Anti-détection)

## 🚀 Installation

### Prérequis
```bash
Python 3.8+
pip3
```

### 1. Cloner le repository
```bash
git clone https://github.com/yourusername/raven-trace.git
cd raven-trace
```

### 2. Créer un environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r raven_trace/requirements.txt
```

### 4. Installer RavenTrace
```bash
pip install -e .
```

## 📖 Utilisation

### Mode Ligne de Commande

#### Recherche par Email
```bash
raven-trace email user@example.com
raven-trace email user@example.com --deep --export json
```

#### Recherche par Téléphone
```bash
raven-trace phone +33612345678
raven-trace phone +33612345678 --country FR --deep --export html
```

#### Recherche par Pseudo
```bash
raven-trace username john_doe
raven-trace username john_doe --deep --export csv
```

#### Batch Search
```bash
raven-trace batch test@example.com john_doe +33612345678
```

### Mode Interactif
```bash
raven-trace interactive
```

Menu complet avec :
- 🔍 Recherche Email
- 📱 Recherche Téléphone
- 👤 Recherche Pseudo
- 🔗 Recherche Combinée
- 📊 Historique
- ⚙️ Configuration
- 🆘 Aide

### Options Globales
```bash
--deep           # Deep scan (toutes les sources, sans cache)
--export json    # Format export (json, csv, html)
--country FR     # Code pays pour téléphone
```

## 💻 API Python

### Exemple Basique
```python
from raven_trace.core.engine import SearchEngine

engine = SearchEngine()

# Recherche Email
email_results = engine.search_email("test@example.com")

# Recherche Téléphone
phone_results = engine.search_phone("+33612345678", country="FR")

# Recherche Username
username_results = engine.search_username("john_doe")

# Afficher confiance
print(f"Confiance: {email_results['confidence']}%")
```

### Affichage des Résultats
```python
from raven_trace.utils.formatter import format_results, create_results_table

# Format texte avec Rich
output = format_results(email_results)
print(output)

# Tableau récapitulatif
create_results_table(email_results)
```

### Export des Résultats
```python
from raven_trace.utils.formatter import export_json, export_csv, export_html

# JSON
export_json(email_results, "/path/to/results.json")

# CSV
export_csv(email_results, "/path/to/results.csv")

# HTML (Rapport complet)
export_html(email_results, "/path/to/report.html")
```

### Rapports Détaillés
```python
from raven_trace.modules.reporting import ReportGenerator

generator = ReportGenerator()

# Générer rapport email
report_path = generator.generate_email_report(email_results)

# Avec recommandations
recommendations = generator._get_email_recommendations(email_results)
for rec in recommendations:
    print(f"- {rec}")
```

### Statistiques
```python
from raven_trace.modules.reporting import StatisticsCollector

collector = StatisticsCollector()

# Enregistrer une recherche
collector.record_search('email', email_results)

# Afficher stats
stats = collector.get_statistics()
print(f"Total searches: {stats['total_searches']}")
print(f"Average confidence: {stats['average_confidence']}%")
```

## 🏗️ Architecture

```
raven-trace/
├── raven_trace/
│   ├── __init__.py
│   ├── main.py              # CLI principale
│   ├── config.py            # Gestion configuration
│   ├── cli/
│   │   ├── __init__.py
│   │   └── interface.py     # Interface CLI
│   ├── core/
│   │   ├── engine.py        # Moteur de recherche
│   │   ├── validators.py    # Validation inputs
│   │   └── scrapers.py      # Scrapers personnalisés
│   ├── modules/
│   │   ├── email_lookup.py  # Recherche email
│   │   ├── phone_lookup.py  # Recherche téléphone
│   │   ├── username_lookup.py # Recherche username
│   │   ├── breaches.py      # Vérification fuites
│   │   └── reporting.py     # Rapports & stats
│   ├── sources/
│   │   ├── public_apis.py   # APIs publiques
│   │   ├── social_media.py  # Réseaux sociaux
│   │   └── data_aggregators.py # Agrégateurs
│   ├── storage/
│   │   └── database.py      # Cache SQLite
│   └── utils/
│       ├── formatter.py     # Formatage résultats
│       ├── logger.py        # Logging avancé
│       └── helpers.py       # Utilitaires
├── requirements.txt
├── setup.py
└── README.md
```

## 🔍 Sources de Données

### Email
- ✅ **EmailRep.io** - Réputation email
- ✅ **Have I Been Pwned** - Fuites de données
- ✅ **DNS Records** - Configuration domaine
- ✅ **WHOIS** - Enregistrement domaine
- ✅ **LinkedIn, GitHub, Twitter** - Profils sociaux

### Téléphone
- ✅ **Phonenumbers** - Validation & localisation
- ✅ **TrueCaller** - Identification numéro
- ✅ **NumVerify** - Vérification numéro
- ✅ **WhitePages, Spokeo** - Agrégateurs données

### Username
- ✅ **GitHub API** - Profils & repos
- ✅ **Reddit API** - Karma & posts
- ✅ **20+ Réseaux Sociaux** - Vérification existence
- ✅ **Forums** - StackOverflow, Medium, Dev.to

## 📊 Format Résultats

### Email Result
```json
{
  "email": "test@example.com",
  "confidence": 85.5,
  "reputation": {...},
  "dns": {...},
  "breaches": [...],
  "domain": {...},
  "social_profiles": [...],
  "timestamp": "2025-01-15T10:30:00"
}
```

### Username Result
```json
{
  "username": "john_doe",
  "profiles_found": 12,
  "social_media": [...],
  "code_repositories": [...],
  "forums": [...],
  "confidence": 90.0,
  "timestamp": "2025-01-15T10:30:00"
}
```

## ⚙️ Configuration

### Fichier config.yaml
```yaml
search:
  timeout: 10
  workers: 5
  rotate_user_agent: true
  rate_limit: 30

cache:
  ttl_hours: 24
  auto_cleanup: true
  cleanup_days: 7

output:
  default_format: table
  show_confidence: true
  show_breaches: true
```

### Variables d'Environnement
```bash
export SHODAN_API_KEY="your_key"
export HUNTER_API_KEY="your_key"
export CLEARBIT_API_KEY="your_key"
```

## 📁 Fichiers Créés

RavenTrace crée automatiquement :
```
~/.raven_trace/
├── cache/          # Cache SQLite
├── logs/           # Fichiers logs
├── exports/        # Fichiers exportés
└── reports/        # Rapports générés
```

## 🔒 Avertissements Légaux

⚠️ **IMPORTANT** ⚠️

RavenTrace est un outil OSINT éducatif. L'utilisateur est **SEUL RESPONSABLE** de son utilisation.

### Utilisation Légale Uniquement
- ✅ Recherche personnelle et éducative
- ✅ Sécurité informatique professionnelle
- ✅ Audit de données avec consentement
- ❌ Harcèlement ou menaces
- ❌ Violation de vie privée
- ❌ Accès non autorisé à données

### Conformité
- 🔐 Respecter le **RGPD** et lois locales
- 📋 Vérifier les **Terms of Service** des sources
- 🛡️ Pas de scraping agressif
- ⚖️ Respecter les **rate limits**

## 🐛 Troubleshooting

### Erreur DNS
```bash
pip install dnspython
```

### Timeout des requêtes
```python
engine = SearchEngine(max_workers=3)  # Réduire workers
```

### Cache plein
```bash
raven-trace clear-cache
```

## 📈 Statistiques Principales

- **20+ Plateformes** supportées
- **50+ Sources** de données
- **Recherche Parallélisée** (5 workers)
- **Cache Intelligent** (24h TTL)
- **3 Formats Export** (JSON, CSV, HTML)

## 🤝 Contribution

Les contributions sont bienvenues ! 

## 📝 License

MIT License © 2025 Samy - Nyx

## 📞 Support

Pour les questions ou bugs :
- 🐛 GitHub Issues
- 📧 Email: Samy.bensalem@etik.com

---

**RavenTrace** - Reconnaissance Intelligente. Utilisez responsablement. 🐦